# Versioned Encounter Lessons

Use this file only for the encounter currently being planned or played. Live
state and current rules text outrank every entry.

## Evidence labels

- `observed`: confirmed by settled API state or actual resolution on the named build.
- `inferred`: supported by branch comparison but not isolated as a rule.
- `guide_prior`: external advice not yet reproduced locally.
- `stale`: contradicted by or unverified on a newer build.

Never silently upgrade `inferred`, `guide_prior`, or `stale` evidence to an
observed rule. Add the build, seed or run, and the decisive before/after state.

## ENCOUNTER.AEONGLASS_BOSS

### Build v0.107.1 — observed

Source: A10 Defect run `NK155CMRBU`, defeated on floor 48.

- `WITHERING_PRESENCE_POWER amount: 0` did not mean inactive. Ending the turn
  resolved an additional upgraded Withering, so treat zero as trigger-ready
  until current text or an isolated probe proves otherwise.
- Withering Presence advanced with cards played. Count every contemplated card
  as a possible trigger advance; a zero-cost card or cantrip is not free in this
  matchup.
- The decisive state contained 58 HP, 30 Block, a 47-damage enemy attack, three
  visible Withering+3 cards dealing 12 each, and one queued 12-damage Withering.
  Total threat was 95, post-Block damage was 65, and survival margin was -7.
- On turn 10 the boss still had 126 of 535 HP and had reached 15 Strength. The
  tested deck's Buffer/Echo setup had a later survival clock than hallway
  fights but an earlier survival clock than its boss lethal.

### Build v0.107.1 — inferred strategy

- Preserve a low-play-count line. Prefer high output per card and re-audit when
  the counter approaches zero instead of finishing a long sequence first.
- Treat Buffer as hit prevention, not a turn of immunity. Status damage and
  multi-hit sequences can spend charges before the largest attack.
- Reserve next-turn energy or retrieval when it changes the first collapse
  turn. In the recorded branches, preserving upgraded Production for a later
  Hologram retrieval materially improved turn-10 resources.
- Plan resources across any following boss form or encounter, but do not save a
  potion that is required to survive the current verified spike.

## ENCOUNTER.EXPERIMENTAL_SUBJECT_BOSS

### Build unknown — observed A10 Ironclad run

- The encounter has multiple forms. A lethal can temporarily leave
  `battle.enemies` empty while combat remains active. Do not report victory or
  attack an empty list. Self-targeted healing may resolve before `end_turn`
  advances the revival.
- The first form can gain Strength whenever a Skill is played. Prefer
  attack-only turns when they solve incoming damage.
- The second form was observed escalating from `11x3` and adding a Wound for
  each attack instance that dealt unblocked damage. Full Block prevented both
  HP loss and draw-pile pollution in the observed build.
- Tungsten Rod applied to each unblocked hit. Reducing a remaining 1 damage to
  zero also prevented the observed Wound trigger.
- A replaying upgraded Defend showing `20 Block, Replay 1` resolved as 30 total
  with Dexterity and Unmovable: 20 for the doubled first segment and 10 for the
  replay. Repoll actual Block instead of multiplying the preview twice.
- The final form alternated Intangible and vulnerable windows and injected five
  Status cards at once. Preserve Block, draw, exhaust, or a potion for the
  post-Status hand and plan HP across all forms rather than one health bar.
