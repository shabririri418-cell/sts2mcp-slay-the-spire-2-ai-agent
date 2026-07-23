---
name: sts2mcp-slay-the-spire-2-ai-agent
description: Control, automate, troubleshoot, and complete Slay the Spire 2 runs through the STS2MCP localhost REST API or MCP server. Use for installation, game-state inspection, combat, map routing, rewards, shops, events, rest sites, save-and-load retries, run verification, or AI-agent gameplay commentary.
---

# STS2MCP Slay the Spire 2 Agent

Control the game through structured state and actions. Optimize for completing the run, preserving HP, and keeping every decision auditable.

## Required references

- Before controlling a run, read [references/api-runtime-and-sl.md](references/api-runtime-and-sl.md) completely. It contains the current REST schema, state machine, timing, recovery rules, and save/load procedure.
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

Expect a response such as `Hello from STS2 MCP v0.4.0`. Match the mod build to the installed game build. Treat older examples that use `/api/v1/state` and `/api/v1/action` as obsolete unless the running server confirms them.

Optional MCP server:

```bash
git clone https://github.com/Gennadiyev/STS2MCP.git
cd STS2MCP
uv run --directory mcp python server.py --help
```

Configure the client with an absolute `uv` path when GUI applications do not inherit the shell `PATH`.

## Core loop

1. Read `GET /api/v1/singleplayer?format=json`.
2. Identify `state_type` and only issue an action valid for that state.
3. Complete the calculation internally, then expose only the decision-critical result in one concise update.
4. POST one action to `/api/v1/singleplayer`.
5. Wait for animation, repoll, and rebuild all indexes and entity IDs.
6. Continue until the run history proves `win: true` or proves defeat.

Do not batch decisions that depend on mutable hand, reward, shop, or selection indexes.

## Strategic priorities

Use state-derived calculations, not generic card-tier assumptions:

1. Prevent lethal and permanent losses such as max-HP damage.
2. Calculate incoming damage after block, multi-hit effects, weak, vulnerable, strength, plating, and relic limits.
3. Check whether killing or disabling an attacker prevents more damage than blocking.
4. Account for energy refunds, zero-cost follow-ups, X-cost modifiers, exhaust triggers, and generated cards.
5. Develop scaling when the current turn is safe; otherwise solve the current turn.
6. Route for expected survival value: rest sites, shops with enough gold or relevant relics, treasure, then manageable elites.
7. Keep high-value potions for unavoidable spikes, elites, and bosses unless using one prevents permanent damage.

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

- Poll at roughly 1 Hz or slower while waiting.
- Treat a successful POST as queued input, not proof that the effect resolved.
- If state does not advance, do not repeat actions blindly. Repoll and inspect `state_type`, `is_play_phase`, selection overlays, energy, and hand indexes.
- For a reproducible API defect, preserve the run, record the exact state/action/response, and fix or update the mod rather than switching to screen control.
- In multiplayer, use the multiplayer endpoint and assume beta-level synchronization risk.

## Upstream

- Mod and server: [Gennadiyev/STS2MCP](https://github.com/Gennadiyev/STS2MCP)
- Original skill source: [Aradotso/mcp-skills](https://github.com/Aradotso/mcp-skills/tree/main/skills/sts2mcp-slay-the-spire-2-ai-agent)
