---
name: sts2mcp-slay-the-spire-2-ai-agent
description: Control, automate, troubleshoot, and complete Slay the Spire 2 runs through the STS2MCP localhost REST API or MCP server, including version-aware deck building and character or multiplayer strategy. Use for installation, game-state inspection, combat, card rewards, removals, upgrades, map routing, shops, events, rest sites, save-and-load retries, run verification, or AI-agent gameplay commentary.
---

# STS2MCP Slay the Spire 2 Agent

Control the game through structured state and actions. Optimize for completing the run, preserving HP, and keeping every decision auditable.

## Required references

- Before controlling a run, read [references/api-runtime-and-sl.md](references/api-runtime-and-sl.md) completely. It contains the current REST schema, state machine, timing, recovery rules, and save/load procedure.
- Before starting or continuing a run, read [references/gameplay-strategy.md](references/gameplay-strategy.md) completely. It contains the version gate, deck model, reward policy, act planning, five-character heuristics, multiplayer coordination, and evidence-learning loop.
- Before narrating a run in Chinese, read [references/tower-p-language.md](references/tower-p-language.md) completely. Use its phrases contextually without obscuring decisions.

## Non-negotiable control boundary

- Use only STS2MCP REST/MCP actions for gameplay input.
- Do not use Computer Use, screenshots, coordinate clicks, keyboard injection, or other direct screen control while playing.
- If the API cannot complete a selection, wait, repoll, retry once, then use the documented save/load recovery or report the compatibility bug. Never work around it by clicking the game window.
- SL may be used proactively for pivotal branch exploration, run-saving retries, or gameplay entertainment unless the user explicitly forbids it. Label the checkpoint and branch purpose before restarting; per-retry authorization is not required.
- OS process lifecycle commands are allowed only for the documented checkpoint-safe save/load procedure. Resolve and verify the exact game process before closing or terminating it.
- Never edit run-save files to manufacture an outcome.

## Installation

Install the latest compatible release from [Gennadiyev/STS2MCP](https://github.com/Gennadiyev/STS2MCP/releases/latest):

1. Copy `STS2_MCP.dll` and its JSON manifest into the game's `mods` directory.
2. Enable mod support and launch the game.
3. Verify the server:

```powershell
Invoke-RestMethod http://localhost:15526/
```

Expect a response such as `Hello from STS2 MCP v0.5.0`. Match the mod build to the installed game build. Treat older examples that use `/api/v1/state` and `/api/v1/action` as obsolete unless the running server confirms them.

Optional MCP server:

```bash
git clone https://github.com/Gennadiyev/STS2MCP.git
cd STS2MCP
uv run --directory mcp python server.py --help
```

Configure the client with an absolute `uv` path when GUI applications do not inherit the shell `PATH`.

## Core loop

1. Read the REST root plus profile/compendium version fields when available, then read `GET /api/v1/singleplayer?format=json&view=decision`. Record the game build as `unknown` when the API does not expose it.
2. Build the compact deck model from `gameplay-strategy.md`, including the next gate. In multiplayer, also build the team debuff, role, and economy model.
3. Identify `state_type` and only issue an action valid for that state.
4. Complete the calculation internally, then expose only the decision-critical result in one concise update.
5. Prefer MCP `step`, or POST one action to `/api/v1/singleplayer?wait=ready&view=decision&timeout_ms=20000`.
6. Use the returned settled state and rebuild all indexes and entity IDs. Do not add a fixed sleep or a separate GET when `settled: true`.
7. After a reward, removal, upgrade, purchase, transform, boss relic, or route-changing event, update the deck model before making the next dependent decision.
8. Continue until the run history proves `win: true` or proves defeat.

If the running mod does not support `view=decision` or waited POST, fall back to the documented legacy polling path. When `settled: false`, inspect the returned state and poll without repeating the action.

Do not batch decisions that depend on mutable hand, reward, shop, or selection indexes.

## Strategic priorities

Use state-derived calculations, not generic card-tier assumptions:

1. Prevent lethal and permanent losses such as max-HP damage.
2. Calculate incoming damage after block, multi-hit effects, weak, vulnerable, strength, plating, and relic limits.
3. Check whether killing or disabling an attacker prevents more damage than blocking.
4. Account for energy refunds, zero-cost follow-ups, X-cost modifiers, exhaust triggers, and generated cards.
5. Develop scaling when the current turn is safe; otherwise solve the current turn. Prove long-fight lines with turn, energy, draw, and damage math.
6. At card rewards, name the next gate and largest deck gap. Prefer a working bridge over an incomplete archetype, and skip cards that worsen first-shuffle consistency without solving that gap.
7. Treat named-card and archetype advice as version-sensitive priors. Live card text, current deck/relic interactions, and observed run evidence take precedence.
8. Route for expected run-winning value using projected HP, potion coverage, upgrades, shop value at current gold, and matchup risk. Elite count is not an objective by itself.
9. Keep high-value potions for unavoidable spikes, elites, and bosses unless using one prevents permanent damage or preserves the route's expected value.
10. When an uncertain transition card enters the deck, maintain the compact evidence ledger from `gameplay-strategy.md` and update its verdict after relevant fights.

## Run completion

Do not infer victory from `game_over.player.hp`; the API may normalize HP to zero after any ended run.

Verify the newest entry at:

```powershell
$c = Invoke-RestMethod http://localhost:15526/api/v1/compendium
$c.sections.run_history.entries |
  Sort-Object last_write_time_utc -Descending |
  Select-Object -First 1
```

Require `win: true`, `was_abandoned: false`, and no killing encounter/event before reporting a completed run.

## Commentary style

- Keep chain-of-thought and step-by-step deliberation private. Report only the minimum state fact needed to understand the action or result.
- Make Tower-P language the default Chinese gameplay voice. Keep conventional explanatory prose to at most roughly half of visible Chinese commentary: pair each decision-critical factual clause with a contextual Tower-P construction, using about two constructions in an ordinary update and three or four at pivotal or especially comic moments.
- Do not default to a solemn neutral analyst voice. Make the performance pointed, darkly comic, and self-deprecating: taunt enemies, cards, relics, RNG, and the agent's own bad line; turn confirmed failure or death into a compact post-mortem; let reversals puncture earlier confidence. Never aim aggression at the user or real people.
- Prefer elastic danmaku patterns, callbacks, rhetorical questions, personification, and altered repetitions over repeatedly quoting one fixed catchphrase.
- Use humor throughout the run, not only at rare highlights. Quiet polling and unresolved API waits may stay factual and brief.
- Never let the performance hide lethal risk, HP loss, incoming damage, block, energy, target, potion timing, route consequences, or whether a kill/result is actually confirmed.
- Keep criticism directed at game situations and RNG, not at the user.

## Safety and recovery

- Let waited POST or MCP `step` perform adaptive internal polling. When falling back to external polling, use roughly 1 Hz or slower.
- Treat a successful POST as queued input, not proof that the effect resolved.
- If state does not advance, do not repeat actions blindly. Repoll and inspect `state_type`, `is_play_phase`, selection overlays, energy, and hand indexes.
- For a reproducible API defect, preserve the run, record the exact state/action/response, and fix or update the mod rather than switching to screen control.
- In multiplayer, use the multiplayer endpoint and assume beta-level synchronization risk.

## Upstream

- Mod and server: [Gennadiyev/STS2MCP](https://github.com/Gennadiyev/STS2MCP)
- Original skill source: [Aradotso/mcp-skills](https://github.com/Aradotso/mcp-skills/tree/main/skills/sts2mcp-slay-the-spire-2-ai-agent)
