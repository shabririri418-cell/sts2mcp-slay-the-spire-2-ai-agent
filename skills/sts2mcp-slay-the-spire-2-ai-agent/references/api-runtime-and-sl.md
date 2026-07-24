# Runtime, State Machine, and SL

Read this file completely before controlling a run.

## Contents

- Current REST surface and common actions
- Timing, turn locks, and selection states
- Merchant-event potion timing and observed API issues
- Save/load checkpoints, relaunch diagnosis, and timeline changes
- Mechanic-first branch escalation
- Victory verification

## Current REST surface

Base URL: `http://localhost:15526`

```text
GET  /api/v1/singleplayer?format=json&view=decision
POST /api/v1/singleplayer?wait=ready&view=decision&timeout_ms=20000
GET  /api/v1/profile
GET  /api/v1/compendium
GET  /api/v1/wiki?query=...
GET  /api/v1/profiles
POST /api/v1/profiles
```

The running `v0.5.0` server uses the same `/singleplayer` endpoint for state and actions. Prefer the compact `view=decision` state. Waited POST returns the post-action state, so rebuild card, reward, selection, shop indexes, and entity IDs from that response. Use a separate GET only for initial inspection, recovery, or when `settled` is false.

Waited POST responses include `action_id`, `settled`, `wait_ms`, `poll_count`, and `state`. State responses include `state_revision`, `actions_enabled`, and `action_state`. A successful raw POST still means only that input was queued; a waited POST with `settled: true` confirms that the returned state is ready for the next decision.

## Common actions

```json
{"action":"play_card","card_index":2,"target":"ENEMY_ENTITY_ID"}
{"action":"use_potion","slot":1,"target":"ENEMY_ENTITY_ID"}
{"action":"discard_potion","slot":0}
{"action":"end_turn"}
{"action":"choose_map_node","index":0}
{"action":"choose_event_option","index":1}
{"action":"choose_rest_option","index":0}
{"action":"claim_reward","index":0}
{"action":"select_card_reward","card_index":1}
{"action":"skip_card_reward"}
{"action":"select_card","index":4}
{"action":"confirm_selection"}
{"action":"combat_select_card","card_index":0}
{"action":"combat_confirm_selection"}
{"action":"shop_purchase","index":7}
{"action":"claim_treasure_relic","index":0}
{"action":"proceed"}
{"action":"menu_select","option":"continue"}
```

Use `target` only when the card or potion requires an enemy. Use the current `entity_id`, not a stale combat index.

## Timing and turn-lock rules

- Prefer MCP `step` or waited POST. Its internal polling starts at `75 ms`, backs off to `150 ms`, then `300 ms`, and returns as soon as a changed state is stable and actionable.
- Use `timeout_ms=20000` normally and at most `30000` for shop-wide automatic acquisition or long relic-triggered selections.
- Do not add a fixed sleep or a redundant GET after a waited response with `settled: true`.
- If only the legacy v0.4.0 API is available, wait `900-1500 ms` after ordinary actions, `5-6 s` after turn/combat-ending or multi-step effects, and `10-15 s` for shop-wide acquisition.
- Before ending a turn, require `battle.turn == "player"`, `battle.is_play_phase == true`, and an ordinary combat state rather than a selection overlay.
- Require `actions_enabled: true`. If `action_state.player_actions_disabled` or `action_state.hand_busy` is true, wait and repoll; do not send another action.

The previous turn-lock failure came from ending turns while a card animation or selection mode still owned the hand. State-driven settlement and action gating prevent it without paying the worst-case delay on every action.

### Deterministic end-turn auditor

Normalize the settled live state into an ordered ledger and run:

```powershell
py -3 <skill-path>\scripts\audit_turn.py <ledger.json>
```

Use this input shape:

```json
{
  "player_hp": 58,
  "current_block": 30,
  "buffer_charges": 0,
  "damage_packets": [
    {"source": "visible Status", "category": "status", "damage": 12, "hits": 3, "order": 0},
    {"source": "enemy attack", "category": "enemy", "damage": 47, "hits": 1, "order": 2}
  ],
  "pending_counter_triggers": [
    {"source": "delayed Status", "counter": 0, "category": "queued", "damage": 12, "hits": 1, "order": 1}
  ],
  "unknown_effects": []
}
```

Supply post-modifier damage per hit and the real resolution order from current
rules or observed state. Categories are `enemy`, `status`, `queued`, or
`other`. Exit code `0` means the fully known ledger leaves positive HP; `1`
means lethal, exact-zero HP, or unknown effects; `2` means invalid input. When
effects are unknown, `worst_case_total` and `survival_margin` are `null`; do not
use the known-damage subtotal as proof of safety.

## Selection-state matrix

| `state_type` | Action | Notes |
|---|---|---|
| `card_reward` | `select_card_reward(card_index)` | Reward indexes are not card indexes. |
| `card_select` single preview | `select_card(index)`, then `confirm_selection` | Poll for `preview_showing: true`. |
| `card_select` choose-one | `select_card(index)` | Combat pile choices such as Headbutt often close immediately; do not confirm. |
| `hand_select` | `combat_select_card(card_index)`, then `combat_confirm_selection` | Burning Pact and similar hand effects use this path. |
| `rewards` | `claim_reward(index)` | Re-fetch after every claim; remaining indexes compact. |

Known compatibility bug: `NDeckEnchantSelectScreen` may acknowledge three `select_card` calls and `confirm_selection` while remaining open. Never click the game window. Poll, retry confirmation once after a delay, then SL/restart. If the same checkpoint reproduces the defect, stop and update/fix the mod's confirm handling before continuing.

## 污浊药水 (Tainted Potion) timing in merchant events

Use the following order whenever 污浊药水 (Tainted Potion) must target the merchant. This is a strict event-state requirement, not an optimization preference:

1. Enter the merchant event and remain on the pre-purchase event screen. Do **not** choose the option that opens the shop inventory yet.
2. Refresh state and confirm that the merchant is still exposed as a valid target. Read its current `entity_id`; never reuse an ID from an earlier state.
3. Use the potion while that merchant target exists:

```json
{"action":"use_potion","slot":0,"target":"MERCHANT_ENTITY_ID"}
```

4. Wait for resolution and refresh state. Confirm that the potion was consumed and its effect resolved before continuing.
5. Only then choose the event option/action that enters the purchase screen.

Do not open the purchase screen first: that screen removes the merchant target needed by the potion. Do not blindly leave and re-enter the shop, because exiting may advance or end the event. If already on the purchase screen, use the potion only after a reversible exit has been confirmed by state and the merchant target has reappeared; otherwise preserve the potion and report that the valid targeting window was missed.

## Issues observed in a complete run

- A successful POST only means the input was queued. Confirm HP, energy, hand, enemy HP, and `state_type` afterward.
- Headbutt opens `NCombatPileCardSelectScreen` as `card_select`, not `hand_select`.
- Burning Pact opens `hand_select` and requires `card_index`, not `index`.
- Card rewards require `select_card_reward` with `card_index`; `choose_card` is invalid.
- Relic and potion acquisition animations can reorder or temporarily hide state.
- Lord's Parasol acquires shop cards and relics sequentially without spending gold. A full potion belt can leave potions stocked and stall the sequence. Discard only the potion chosen for replacement, repoll, and purchase manually if automatic acquisition does not resume.
- A shop can accept `proceed` even when `shop.can_proceed` is false after all relevant stock is resolved.
- Chemical X adds two effect counts even when a generated X-cost card is played for zero energy.
- Post-run `game_over.player.hp == 0` does not prove death. The newest run-history entry is authoritative.
- `compendium.current_run.is_in_progress` can lag immediately after the ending; prefer `sections.run_history.entries`.

## Save/load timeline technique

Use SL proactively when a pivotal branch is lost, a different RNG-consuming order may materially improve the run, an API defect requires recovery, or a retry adds useful gameplay entertainment. Per-use user authorization is not required unless the user has explicitly prohibited SL. Treat it as controlled branch exploration, not as save-file editing, and announce the checkpoint and objective before restarting.

Slay the Spire 2 automatically checkpoints at the beginning of combats and events. Exploit that boundary as follows:

1. At the untouched combat/event start, wait for saving to finish and record floor, room/event ID, HP, deck/relic state, enemies/options, hand, and intents.
2. Try one clearly labeled branch and record its actions and outcome.
3. To reject the branch, exit before entering another room or creating a later checkpoint. Do not choose the next map node.
4. Prefer a graceful window close through the OS process API. Verify the exact game PID and executable path, request a normal window close, and wait until both the process and `http://localhost:15526/` are gone before relaunching.
5. Relaunch through the same Steam context that started the working modded process, wait for the REST server, then use `menu_select` with `option: "continue"`. Prefer Steam's `-applaunch APP_ID` when a direct executable launch cannot initialize Steamworks.
6. Verify that floor, room/event, HP, enemies/options, and initial hand match the recorded checkpoint before trying another branch.
7. Stop retrying when the improvement is negligible, the same deterministic result repeats, or restart stability degrades.

Do not force-kill while a save icon, reward transition, or room transition is active. Use forced process termination only after graceful close fails, the exact game PID and path have been verified, and the current state is a known checkpoint-safe SL boundary.

### Relaunch diagnosis

- Record the working process path, parent process, and command line before the first restart. A visible, responsive game process does not prove that Steamworks or the mod loaded; the REST endpoint is authoritative.
- If the log reports `No appID found`, close that failed direct-launch process before asking Steam to launch the app. Otherwise Steam may treat the broken process as the already-running game and ignore the new request.
- Discover the Steam AppID from `appmanifest_*.acf` and the Steam client path from the local Steam configuration. Launch with `steam.exe -applaunch APP_ID`, then poll the REST root. Do not hardcode machine-specific paths in reusable automation.
- If the process survives but the REST server never appears, inspect the newest game log for Steam initialization and mod-loading lines before retrying. Do not interact with an error popup through mouse or keyboard automation.

### Changing the timeline

Reloading and repeating identical actions normally reproduces identical outcomes. Change the order or presence of RNG-consuming actions to explore a different branch:

- draw before or after another action;
- change random-target attack order;
- generate a random card before another random effect;
- alter potion timing;
- exhaust a different card;
- choose a different event option or card-selection order;
- finish the fight through a different action sequence before checking rewards.

Do not promise a reroll. The game can use separate or fixed RNG streams, so some rewards, upgrades, transforms, intents, or event results remain identical. Record every real reload truthfully in the SL ledger. In Tower-P commentary, `0.5nosl` is the joke told after an actual save/load: `nosl` claims a no-save/load playstyle, while `0.5nosl` stubbornly half-denies the SL that really occurred. It is not a technical label for an unchanged deterministic outcome or for information gathering. State the actual reload and result even when using the joke.

Keep an SL ledger:

```text
checkpoint: act/floor/room
mechanic hypothesis: exact trigger/timing being tested
branch A: actions -> HP/reward/result
branch B: actions -> HP/reward/result
worst threat: visible + Status + queued + unknown
chosen: branch X, objective reason
restarts: N
```

Prefer the branch with the best run-winning probability, not merely the flashiest immediate roll.

### Mechanic-first branch escalation

- When two branches fail to the same trigger or transition, stop making only
  local action-order permutations. Promote the shared failure to a mechanic
  hypothesis and branch from the earliest turn that can change its counter,
  resource reservation, Status inflow, or kill clock.
- When timing or rules text is uncertain, use one minimal probe branch to learn
  the trigger. Record the exact before/after state and real reload. Do not mix a
  mechanic experiment with an unrelated high-roll search.
- Re-run the end-turn audit for every branch. Comparing enemy HP alone is
  insufficient; record survival margin, queued damage, potion state, and the
  next-turn hand or draw consequence.
- Stop when the mechanic is stable and every earlier meaningful branch has the
  same proven loss. More retries are not evidence when they change no relevant
  variable.

## Victory verification

```powershell
$c = Invoke-RestMethod 'http://localhost:15526/api/v1/compendium'
$latest = $c.sections.run_history.entries |
  Sort-Object last_write_time_utc -Descending |
  Select-Object -First 1
$latest | Select-Object win,was_abandoned,killed_by_encounter,killed_by_event,ascension,seed
```

Report victory only when `win` is true and `was_abandoned` is false.
