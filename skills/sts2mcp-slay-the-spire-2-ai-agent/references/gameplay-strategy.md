# Gameplay Strategy and Evidence

Read this file completely before starting or continuing a run. It supplies the
deck-building policy behind card rewards, removals, upgrades, routing, shops,
and multiplayer coordination. Live state and current card text always outrank
the guide-derived heuristics below.

## Version gate

1. Read the game/build version from the REST root, profile, compendium, or run
   state when exposed. Otherwise label the build `unknown` in the internal run
   ledger.
2. Use current API card descriptions, costs, values, keywords, and upgrade
   deltas for all calculations. Never substitute remembered numbers.
3. Treat named-card advice as a hypothesis when its source predates the current
   build. Re-evaluate it against the live text and current encounter pool.
4. Do not use a guide's archetype label as proof that a card belongs in the
   deck. A card must solve a present gap or strengthen an engine already likely
   to function.

This guard is material: the public title of the recommended Necrobinder
"10-minute" guide now explicitly says its v0.099 advice is obsolete, while a
newer Defect guide is labeled for v0.107-v0.108. Do not silently mix those
patches.

## Deck model

Maintain this compact model after every reward, shop, event, boss relic, and
meaningful transform:

```text
next_gate: next elite/boss or known dangerous hallway fight
frontload: single-target / area damage available in first shuffle
defense: block / weak / strength reduction / prevention and its timing
scaling: damage and defense growth by turns 3, 6, and 10
engine: energy / draw / generation / exhaust-discard-orb support
consistency: deck size / opening dead draws / status tolerance
sustain: current HP / healing / potion coverage
upgrade_pressure: critical upgrades still waiting
```

For multiplayer, append:

```text
team_debuffs: vulnerable / weak / expose / strength reduction uptime
team_roles: each player's damage, defense, setup, and finisher contribution
team_economy: gold distribution and any known wealth-sensitive event plan
```

At a card reward, apply this order:

1. Name the next gate and the deck's largest quantified gap.
2. Evaluate each card's first-shuffle value, later-shuffle value, energy and draw
   burden, upgrade demand, and interaction with relics and current cards.
3. Prefer a card that materially clears the next gate even if it is only a
   bridge. A working transition card is more valuable than an incomplete
   endgame package.
4. Prefer flexible cards when two choices solve the gate similarly. Flexibility
   includes useful targeting, draw, energy smoothing, exhaust/discard access,
   or multiple defensive modes.
5. Take speculative scaling only when the deck can survive while setting it up.
6. Skip when every choice is redundant, too slow, or worsens the first shuffle
   more than it improves the named gate.

Do not force a thin deck or a fixed card count. Measure effective consistency:
a larger deck with draw, energy, and status control can be more reliable than a
small deck containing irremovable liabilities.

## Evidence policy

Use guide claims with asymmetric but critical scrutiny:

- A strong-card claim from a player who repeatedly took and demonstrated the
  card is useful positive evidence. Test the stated job and setup against the
  live deck.
- A weak-card claim from a player who normally skips the card is weak negative
  evidence. It may be theory rather than observed play.
- A forced transform, poor reward screen, or high-pressure bridge pick is an
  experiment. Record what the card actually did instead of preserving its old
  reputation.
- A single successful anecdote does not establish a universal pick. Separate
  "usable bridge", "conditional engine", and "generally strong".
- Full-card explanations with encounter context are more useful than tier
  images. Live runs are especially useful for transition cards, but one run can
  be distorted by relics or luck.

Keep a short transition-card ledger when an uncertain card is added:

```text
card / build / floor acquired
intended job
drawn in which dangerous fights
energy or draw displaced
damage/block/debuff actually contributed
synergies required
verdict: failed / bridge / conditional engine / broadly strong
```

Update the verdict after relevant fights. Do not spam visible commentary with
the ledger; report only when it changes a decision.

## Run planning

### Act 1

- Buy enough immediate single-target damage and defense to take the planned
  early fights and elites. Do not wait for a named archetype.
- Add area damage when the route or known encounter pool demands it.
- Spend upgrades on the card that most improves the next gate. Do not reserve a
  campfire upgrade for a hypothetical future card.
- Take an elite only when current HP, potions, and the first-shuffle model give
  a credible line through its worst relevant pattern. More elites are not an
  objective by themselves.

### Act 2

- Require a real answer to group fights, status pollution, and faster incoming
  damage.
- Add scaling or a reusable engine before the boss, but reject engines that make
  the first two turns collapse.
- Reassess transition cards: remove or exhaust the bridges whose jobs are now
  duplicated; retain bridges that still solve a matchup.

### Act 3 and bosses

- Identify the exact win condition and its setup time. Check damage ceiling,
  defensive endurance, debuff uptime, and bad-draw recovery.
- Value redundancy for the key engine when one status-heavy hand or one lost
  component would otherwise end the run.
- Plan HP and potions across all boss forms, not just the current health bar.

Routing maximizes run-winning probability, not raw rewards. Compare expected HP
after the route, upgrade access, shop value at current gold, potion coverage,
and whether the route exposes the deck to a matchup it has not solved.

## Character heuristics

These are starting priors, not recipes. Verify every named card against current
text and the deck model.

### Ironclad / 战士

Choose between an attack-first and defense-first plan from actual early rewards
and removals:

- Attack-first is the simpler default when early damage, energy, exhaust, and
  draw support appear. Removing Defends can support lines involving 劫掠、完美打、
  跃跃欲试、踩踏. End fights before the defense deficit compounds.
- In a fast attack plan, do not wait for 武装 to upgrade the deck. Upgrade the
  key damage, energy, or setup cards directly; even an unupgraded 耸肩 may be a
  legitimate bridge when the next gate needs block.
- Defense-first is viable when the deck finds a repeatable defensive engine and
  payoff. Removing Strikes can support 重振 or 坚定不移 lines. It still needs a
  credible damage clock.
- Evaluate 血墙 as a usable two-cost transition defense when its block prevents
  a real spike. "Two cost" alone does not imply unacceptable high-ascension HP
  loss.
- Raise confidence in conditional cards such as 残酷 only after identifying the
  concrete trigger density and turns on which it pays back.

Do not combine attack-first removals with a slow defense shell by habit. If the
reward stream forces a pivot, rebuild the deck model and change removals,
upgrades, and routing together.

### Huntress / 猎人

- Prefer poison as the default transitional damage source when available. It
  gives a more independent damage clock than an early knife-only package.
- Treat knives as valuable frontload and an engine component, not automatically
  as the sole damage terminal. Before committing, test the deck against enemies
  that punish repeated attacks, blunt small hits, or demand scaling.
- Corrosion-wave and precision-knife packages are examples, not the only valid
  builds. Preserve weak, draw/discard, and defensive tools that keep setup turns
  alive.
- If relying on one damage family, reserve a potion or add a secondary answer
  for the boss or elite that specifically counters it.

### Regent / 储君

- Simulate yellow/blue energy conversion across the whole turn and the next
  draw. Do not spend one color merely because it is available.
- Value the character's long-fight ceiling, but name a surviving setup line.
  环绕轨道 plus even one 飞溅 output can be enough when energy conversion and
  defense make repeated cycles reliable.
- For imprint cards, use 类星体 as the strongest general prior and 君权自授 as
  a strong one-cost transitional defense prior. Both often justify an early
  upgrade because the upgrade affects the engine, but compare them with the
  next gate before consuming the campfire.
- 光谱（磁力）can be an Act 1 speculative pick in singleplayer when the current
  colorless pool and deck can absorb variance. Avoid it by default in
  multiplayer because multiplayer colorless cards dilute the generated pool;
  reconsider only with current-patch evidence.

Zero draw is not automatically fatal if orbit, conversion, and a repeatable
output form a deterministic long-fight line. Prove the line with turn and energy
math rather than assuming conventional draw requirements.

### Necrobinder / 亡灵契约师

- The main early problem is transition, not theoretical ceiling. Prefer cards
  that produce enough immediate numbers while moving toward bone, palm,
  sacrifice, pact, or familiar interactions.
- Do not force separate "doom" or "summon" archetype labels. Evaluate each card
  by output, setup cost, and overlap with the current engine.
- Treat 血肉尽孝 as a serious power card when the deck can pay two energy and
  exploit its output. Reject the blanket rule that any two-cost card causes
  unacceptable high-ascension damage.
- Use these as bridge candidates when their current text still performs the
  stated job: 能量汲取 for simple scaling and Act 1 boss preparation; 击掌 for
  accessible vulnerable; 碎骨 for early damage; 猛晃 when retrieval support
  exists and to unlock 紧追不放; 拖延 for transitional defense.
- Re-evaluate expensive or setup-heavy death/negative-energy combinations by
  their first-cycle survival, not just their damage ceiling.

The old v0.099 quick guide is evidence about concepts and card roles only. Never
copy its rankings into a later build without checking live text.

### Defect / 故障机器人

- Expect fewer mature guide priors and rely more heavily on the transition-card
  ledger. The character still needs immediate numbers before its orb or ability
  ceiling matters.
- Bridge candidates, subject to current text: 污秽攻击 for early damage and
  enchant-event protection; 眼部 for scarce weak; 高速脱离 for flexible output,
  especially with 万物; 热修复 for baseline sustain/defense; 弹幕齐射 when orbs
  raise its ceiling; 充电 for defense; 旋转工艺 for group fights; 冰之长枪 as an
  awkward but usable last-resort bridge; 骚动 as a partial damage terminal when
  its setup and energy loss are survivable.
- Treat 白噪 as a poor default when random permanent ability generation can
  repeatedly produce dead output. 创造性 AI is likewise unreliable, but can be
  a conditional ceiling with a payoff such as 双子程序 energy generation.
- 回响 remains a strong general ceiling prior because doubling the best action
  is broadly useful; still check setup-turn survival.
- Do not auto-pick 扩容. Long setup, future-status costs, and a faster combat
  plan can make extra orb slots actively mismatched. 雷霆 can further change the
  slot calculation.
- Match 偏差 to the orb plan: it is usually more coherent with a Dark-orb burst
  line than with Lightning consumed by 雷霆 or an Ice plan that intends to play
  a short, aggressive fight. Recalculate from current values.
- Downgrade 循环 when its timing cannot benefit from Focus gained later in the
  same turn. Verify the current timing text before applying this interaction.

Do not reject a two-energy bridge solely on cost. Quantify the HP lost by the
energy displacement and compare it with the fights or boss phases the card
solves.

## Multiplayer

Multiplayer is easier only when players coordinate. Before map, reward, and
boss decisions, share the compact team model through concise commentary.

- Do not build one player as pure defense while others carry all damage. That
  transfers pressure and makes bad draws on either side catastrophic. Every
  deck needs a credible contribution during damage races.
- Debuffs applied to enemies create team-wide value. Count shared uptime rather
  than crediting only the applying character.
- Ironclad gains value from teammates supplying vulnerable because 主宰 can use
  it. Huntress can supply 暴露、虚弱 and 尖啸-style mitigation. Regent can cover
  weak, vulnerable, and strength reduction. Necrobinder's 摧残 and 苦难 gain
  value when paired with reliable burst, poison, or other team payoff.
- Defect's personal strength can remain high, but its relative team contribution
  may fall when other characters supply more globally useful debuffs. Do not
  compensate by forcing a weak support package.
- Avoid multiplayer 光谱 by default because the colorless generation pool is
  diluted. Inspect the current pool before making an exception.
- Coordinate gold spending when a known Act 2 event outcome depends on relative
  wealth. Never sacrifice an immediately necessary shop purchase merely to
  preserve that manipulation.
- In combat, assign target, debuff, defense, and finisher roles before committing
  actions whose value depends on a teammate's later play. Re-read settled state
  after every teammate action because indexes and lethal math can change.

## SL as an experiment

Follow the checkpoint mechanics in `api-runtime-and-sl.md`. Use an SL branch to
answer a concrete question: whether action order changes RNG, whether a bridge
card prevents more HP loss, whether a potion is required, or which target/order
survives the next phase.

Add the deck-model change to the SL ledger:

```text
hypothesis
branch result: HP / turns / potion / deck-model lesson
chosen branch and run-winning reason
```

Stop when the branch no longer teaches anything or improves only cosmetic
damage. Choose difficult stable wins over flashy high-roll lines.

## Source notes

The following public Bilibili pages were checked on 2026-07-23 for title and
version metadata. They are practitioner evidence, not authoritative game data:

- [萌新抓牌攻略上篇](https://www.bilibili.com/video/BV1KkXPBREf8/)
- [战士双百连评卡！攻杀还是防杀？](https://www.bilibili.com/video/BV1Ur9HBGE8u/)
- [战士 A10 连胜攻略](https://www.bilibili.com/video/BV1hqwEzoECM/)
- [猎人轮椅套路](https://www.bilibili.com/video/BV1UYPSzmE23/)
- [储君全评卡＋打法思路讲解](https://www.bilibili.com/video/BV1LvwFzjEi4/)
- [亡灵契约师 10 分速通（页面已标注 v0.099 过期）](https://www.bilibili.com/video/BV1yjwwzTEfs/)
- [30 连胜亡灵契约者抓牌分析](https://www.bilibili.com/video/BV1bzwDz1EvZ/)
- [故障机器人 20 连胜思路](https://www.bilibili.com/video/BV1Z7QrBkESC/)
- [故障机器人全卡评级（v0.107-v0.108）](https://www.bilibili.com/video/BV1FmTC61EU5/)
- [你真的了解骚动这张新卡吗？](https://www.bilibili.com/video/BV1kRXSBVEcJ/)

Use the user's supplied article as the primary synthesis of the videos' detailed
claims. Public pages did not expose a complete transcript during verification,
so do not attribute additional card-specific claims to a video unless directly
observed elsewhere.
