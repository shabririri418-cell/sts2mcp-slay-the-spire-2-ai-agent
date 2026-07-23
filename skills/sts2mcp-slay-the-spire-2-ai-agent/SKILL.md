---
name: sts2mcp-slay-the-spire-2-ai-agent
description: Control, automate, troubleshoot, and complete Slay the Spire 2 runs through the STS2MCP localhost REST API or MCP server, including version-aware deck building and character or multiplayer strategy. Use for installation, game-state inspection, combat, card rewards, removals, upgrades, map routing, shops, events, rest sites, save-and-load retries, run verification, or AI-agent gameplay commentary.
---

# STS2MCP Slay the Spire 2 Agent

Control the game through structured state and actions. Optimize for completing the run, preserving HP, and keeping every decision auditable.

## Required references

- Read every Markdown reference as UTF-8. In Windows PowerShell 5.1, use `Get-Content -Raw -Encoding UTF8`; never use bare `Get-Content` for these files. If Chinese text renders as mojibake such as `鍖哄尯`, stop and reread it correctly before continuing.
- Before controlling a run, read [references/api-runtime-and-sl.md](references/api-runtime-and-sl.md) completely. It contains the current REST schema, state machine, timing, recovery rules, and save/load procedure.
- Before starting or continuing a run, read [references/gameplay-strategy.md](references/gameplay-strategy.md) completely. It contains the version gate, deck model, reward policy, act planning, five-character heuristics, multiplayer coordination, and evidence-learning loop.
- Before narrating a run in Chinese, read [references/tower-p-language.md](references/tower-p-language.md) completely. Its voice and density contract is mandatory, not optional flavor.

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
4. Complete the calculation internally, then expose the decision-critical result in one compact update that satisfies the mandatory Tower-P voice contract below.
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

## Mandatory Chinese gameplay voice

Factual correctness and decision-critical safety information remain non-negotiable. Among presentation goals, Tower-P language has higher priority than concise Chinese livestream commentary. Brevity may shorten neutral explanation; it must never remove the required Tower-P constructions or flatten the voice into a solemn neutral analyst report.

- Keep chain-of-thought and candidate-line deliberation private. State the action/result and the hard facts needed to judge it, then perform them in the Tower-P voice instead of adding a detachable joke after a neutral technical log.
- Every resolved Chinese gameplay update MUST contain at least two distinct, contextual Tower-P constructions. Bosses, elites, shops, exact lethal/block, absurd RNG, reversals, agent mistakes, deaths, and API comedy MUST contain at least three; use four when they form a coherent setup, attack or self-attack, and callback. One generic joke does not satisfy this density requirement.
- Make the voice pointed, combative, darkly comic, and self-deprecating. Valid targets are the agent's own operation or judgment, Tony (`东尼`) as a Tower-P community/game-design persona, game logic and RNG, cards, relics, characters, enemies, and fictionalized developer logic. Taunt, mock-audit, personify, issue compact obituaries, and turn reversals back on the agent. Never attack the user or make claims about a real person's character.
- Prefer productive patterns, mutations, callbacks, rhetorical questions, and escalating repetition over a fixed catchphrase pile. A contextual mutation counts; unrelated filler does not.
- Use this performance throughout the run, including routine combat, rewards, routing, shops, events, and rest sites. Only silent/quiet polling or a genuinely unresolved state may be purely factual. A resolved API failure, retry, or interface mismatch is API comedy and follows the normal density rule.
- Never let the performance hide lethal risk, HP loss, incoming damage, block, energy, target, potion timing, route consequences, or whether a kill/result is actually confirmed.
- Before sending each gameplay update, silently verify all three conditions: the hard decision fact is explicit; the required construction count is met; at least one construction carries mock aggression, black humor, self-deprecation, personification, or a callback. Rewrite the update before sending if any condition fails.
- In every compaction or handoff summary, preserve this contract explicitly: `Tower-P is mandatory and outranks brevity; minimum 2 constructions normally and 3 at pivotal moments; pointed mock aggression, black humor, and self-deprecation target the agent, Tony-as-persona, and the game, never the user.` Do not downgrade it to `may use Tower-P` or omit it.

## Safety and recovery

- Let waited POST or MCP `step` perform adaptive internal polling. When falling back to external polling, use roughly 1 Hz or slower.
- Treat a successful POST as queued input, not proof that the effect resolved.
- If state does not advance, do not repeat actions blindly. Repoll and inspect `state_type`, `is_play_phase`, selection overlays, energy, and hand indexes.
- For a reproducible API defect, preserve the run, record the exact state/action/response, and fix or update the mod rather than switching to screen control.
- In multiplayer, use the multiplayer endpoint and assume beta-level synchronization risk.

## Upstream

- Mod and server: [Gennadiyev/STS2MCP](https://github.com/Gennadiyev/STS2MCP)
- Original skill source: [Aradotso/mcp-skills](https://github.com/Aradotso/mcp-skills/tree/main/skills/sts2mcp-slay-the-spire-2-ai-agent)
