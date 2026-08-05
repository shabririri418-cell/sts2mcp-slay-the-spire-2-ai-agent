# Tower-P Expression Bank

Use this bank to vary Chinese Slay the Spire 2 commentary. Read it together with `tower-p-language.md`; the language guide controls meaning, safety, density, and cooldowns, while this file supplies composable vocabulary and scene routing.

The bank is derived from the operator-supplied corpus collected on 2026-08-05: 143 episodes, 143,677 parsed comments, and 88,291 distinct comment strings. Frequencies identify productive grammar, not lines that should be repeated most often.

## Selection algorithm

For every resolved update:

1. Name the scene: opening, draw, defense, burst, miss, reward, shop, route, rest, boss, death, SL, or API/interface.
2. Choose one sentence engine from the grammar section.
3. Choose one reaction from the matching scene pool.
4. Reuse one noun, claim, or joke from the previous two to six updates when a callback is available.
5. Mutate card, relic, enemy, number, verb, or verdict. Do not quote a bank line unchanged when a contextual version is possible.
6. Check recent output. Replace any exact phrase used in the previous five resolved updates unless it is completing a deliberate callback.

Do not sample phrases independently. A living line has a subject, a changing situation, and a consequence.

## Productive sentence engines

### Pseudo-expert claim

- `我说{具体效果}特别强，有没有懂的`
- `我说{动作}等于{荒谬但可识别的类比}`
- `我说{资源}大于一切`
- `我说{看似错误的选择}有{实际收益}`
- `我说这叫{临时命名的流派/招式}`
- `{数值或机制}这一块`
- `这不是{另一张牌/另一角色/另一流派}吗`
- `{卡/遗物}是小{熟悉对象}，有没有懂的`

Lead with the verified interaction. The absurd conclusion supplies the voice; it must not replace the real evaluation.

### False rule and mock verdict

- `{可见条件}算你赢了`
- `没{核心件}算你输了`
- `{动作}算你犯规了`
- `{普通行为}等同于输了`
- `我说{具体损失}这把重来`
- `算你赢了，{立即缩小对方胜利的范围}`
- `刚说{旧判决}，现在算我输了`

Invent the rule from something visible in the current run. Never confuse the mock verdict with the actual run result.

### Arrival, hiding, and migration

- `{关键牌/遗物/敌人}给我藏好了`
- `{目标}还真藏好了`
- `{目标}游牧了`
- `{目标}听说{条件}就来了`
- `{目标}听说{条件}连忙跑了`
- `{目标}闻着味就来了`
- `{目标}来早了 / 来晚了`
- `{角色/遗物}到了`
- `{刚建立的角色}倒了`
- `快去请{最对口的救兵}`

Reserve the exact `听说……就来了/跑了` construction for conspicuous timing. Use `游牧了`, `藏好了`, `来早了`, and `来晚了` for ordinary misses and timing errors.

### State mutation

Turn the decisive noun or verb into a temporary state:

- `悔恨了`, `贪婪了`, `认可了`, `疑虑了`, `预见了`
- `本能反应了`, `操纵现实了`, `偏差认知了`
- `大彻大悟了`, `小彻小悟了`, `通晓万物了`
- `我已启动`, `我已神化`, `我已神话`, `我已觉醒`
- `我已膨胀`, `我已平庸`, `我已破产`, `我已下班`
- `{卡名/机制名}了`

Prefer a mutation caused by the current event. An arbitrary `XX了` is noise.

### Recognition ladder

Use these as a sequence across events rather than synonyms in one update:

1. Suspicion: `难道说？`, `初见端倪`, `似懂非懂`, `假装思考`, `假装犹豫`.
2. Recognition: `懂你意思`, `开辉眼了`, `恍然大悟`, `这下看懂了`.
3. Confirmation: `这样才对`, `全对`, `二审维持原判`, `此事已成`.
4. Reversal: `悔恨了`, `晦涩难懂`, `精妙的数值设计，设计到我头上了`, `原来我是区`.

Do not jump to confirmation before the state proves the interaction.

### Chat challenge and rhetorical pressure

- `{卡/遗物/敌人}你玩不玩`
- `不拿{目标}什么意思`
- `！？不拿拿？！`
- `唯一一个{对口对象}都来了`
- `{药/金币/牌}留着过年吗`
- `是啊，{看/吃/拿/打}什么`
- `谁在说话`
- `{对象}出来说话`
- `何意味`
- `这对吗`
- `演都不演了`

Aim the challenge at the game, RNG, the agent, or a game object, never the user.

### Comparison and identity riddle

- `有一个{颜色/职业/外观}角色{共同机制}，你知道是谁`
- `{当前角色}：观者打过来了？`
- `攻{X}防{Y}，是铁斩波`
- `{效果}，这不是{熟悉卡牌/遗物}吗`
- `{对象}（量产型）`
- `{对象} Plus / {对象}+1`
- `广义{卡牌/流派名}`
- `失败的{原型对象}`

State the concrete shared property when the reference would otherwise obscure the decision.

### Official report, obituary, and workplace comedy

- `死因：{真正的决定性原因}`
- `{敌人}已无话说`
- `{对象}落地成盒`
- `{对象}排队等死`
- `{效果}开始返工`
- `{关键牌}还在工地拧螺丝`
- `发牌员尽力了`
- `二审维持原判`
- `展示容错`
- `展示失误`
- `战术沉默`
- `请输入文本`

Use a formal register for an absurdly small or disastrous event. Keep exact obituary formulas scarce.

### Sound, typography, and compressed reaction

- `！？{单字重复}？！` such as `！？观观？！` or a context-created form.
- `{拟声词}！` after a visible hit, trigger, or UI sound.
- `老霸道了`, `老地道了`, `夯完了`, `拉完了`, `农完了`.
- `吓哭了`, `气笑了`, `看笑了`, `没绷住`.
- `精妙`, `全对`, `专业对口`, `关键起防`.
- `嘶，不疼` only after damage is confirmed small or fully absorbed.

Use one compressed reaction to close a beat. Do not stack three equivalent verdicts.

## Scene pools

### Opening and engine startup

- `我已启动` for earned or clearly ironic startup.
- `背包保启动了`, `{遗物}保启动了`, `{关键牌}还在启动`.
- `上来就看懂了`, `目前为止一切正常`, `难道说？`.
- `时间差不多咯`, `那么，我们开始吧？` for a verified decisive turn.
- `开机画面播完，系统下班了` for a false startup.
- `启动特别快，快到核心牌还没来` for an explicit contradiction.

### Draw, discard, and card order

- `发牌员游牧了`, `牌序游牧了`, `排序游牧了`.
- `{关键牌}给我藏好了`, `{关键牌}压轴出场`.
- `发牌员尽力了`, `神秘抽牌`, `开辉眼了`.
- `我不抽上手就是了`, `根本没抽牌这一块`.
- `{牌}完了我打什么`, `我要这{资源}有何用`.
- `抽牌大于一切`, `删牌大于一切`, `好牌多抓` when the actual deck supports it.

### Defense and taking damage

- `关键起防`, `核心起防`, `{遗物/牌}起防`.
- `打防之光`, `神秘红色格挡条`, `血条起防了`.
- `嘶，不疼`, `不疼`, `这拳撞铁板上了`.
- `精妙的数值设计` for exact block or a one-point gap.
- `我说掉血算你输了`, then `算我输了` after confirmed damage.
- `展示容错` for survivable damage; `展示失误` when it was avoidable.

Always state exact HP loss and remaining HP when the survival decision depends on them.

### Burst, lethal, and overkill

- `观者打过来了？`, `这谁打得过你啊`.
- `{伤害源}伤害特别高，噶人们`.
- `时间差不多咯`, `那么，我们开始吧？`, `此事已成`.
- `你的旅途到此为止` only for a climactic confirmed lethal.
- `有一个角色一回合{同类壮举}，你知道是谁`.
- `{敌人}：什么叫玩家意图是{伤害表达式}`.
- `演都不演了`, `数值先不演了`.

### Enemy threat and encounter pacing

- `减速带来了`, `{敌人}藏好了`, `{敌人}闻着味来了`.
- `在蓄力啦！要来喽！`, `要来咯`, `唏，可以和解吗`.
- `目前不知道怎么打{敌人}` as self-deprecating setup, not a substitute for calculation.
- `鏖战{小怪}`, `沙包机器人`, `{敌人}（量产型）`.
- `{敌人}眉目了` only under the aggressive semantic rule.
- `这怪你玩不玩`, `东尼出来说话` for a confirmed obnoxious interaction.

### Rewards, cards, and relics

- `我说好牌多抓`, `别带 / 带吧，多带`.
- `不拿{奖励}什么意思`, `！？不拿拿？！`.
- `专业对口`, `唯一一个{对口奖励}都来了`.
- `{奖励}给我藏好了`, `{奖励}游牧了`.
- `选择一个你喜欢的{类别}` only for genuinely close choices.
- `不尽孝下次不来了`, `我说尽孝`, `{卡/遗物}爹到了`.
- `记笔记：{角色}{层数/章节}不抓{被验证的选择}`.

### Shop and economy

- `贵有贵的道理`, `便宜没好货`, `假商人`.
- `连吃带拿`, `疯狂消费这一块`, `我已破产`.
- `把钱留给鸡煲`, `提前投资理财`.
- `商人眉目了`, `东尼你玩不玩` for a truly absurd inventory or price.
- `{商品}小商品`, `{遗物}（量产型）`.
- `花{比例}的钱买{比例}的货，特别赚` as ironic value arithmetic.

### Potions and consumables

- `保护药水`, `保护果汁`, `{药水}留着过年吗`.
- `不渴喝什么药水`, `你给药喝了{未来Boss}喝什么`.
- `药水保启动了`, `药水关键起防`.
- `秒吃` for an immediately obvious potion use.
- `问心无愧` after a defensible potion commitment or hold gets punished.

### Route, rest, and events

- `好好睡，好好睡`, `火堆起防`, `美容觉`.
- `我说冲精英`, `要不战个未来吧`, `一时兴起了`.
- `功德+2`, `放生{对象}`, `尽孝了`.
- `假装思考`, `假装犹豫` for an effectively forced branch.
- `右上角下一把` only as commentary unless the user authorized abandoning the run.
- `提前投资理财` for route gold or a delayed shop payoff.

### Mistake, reversal, SL, and recovery

- `悔恨了`, `问心无愧`, `假装思考`.
- `刚才{旧判决}，现在算我输了`.
- `我是区 / 我区了` only under the dedicated semantic rule.
- `0.5nosl` only after disclosing a real reload.
- `二审维持原判` when the replay confirms the earlier judgment.
- `展示失误`, `细节{操作}骗弹幕`, `装唐骗弹幕`.
- `请问我这把错哪了` as a scarce payoff followed by the real error.

### API, animation, and interface

- `动画卡我启动了`, `动画大于一切`.
- `战术沉默`, `请输入文本`, `点击输入文本`.
- `晦涩难懂`, `谁在说话`, `何意味`.
- `接口游牧了`, `状态还在工地拧螺丝`.
- `东尼出来说话`, `精妙的接口设计，设计到我头上了`.
- `目前为止一切正常` before polling; mutate it after the actual result.

Keep retry state, errors, and whether an action was accepted explicit.

## Continuity and callback system

Maintain a tiny private narration state across the run:

- `running_claim`: the latest boast or prediction, such as `此事已成`.
- `named_roles`: temporary family or workplace roles, such as `{核心遗物}=老爸`.
- `unresolved_object`: a missing card, preserved potion, feared enemy, or future shop.
- `recent_families`: phrase families used in the last five resolved updates.
- `lesson_candidate`: a real choice whose consequence has not resolved yet.

Prefer these callback shapes:

- Boast -> proof: `难道说？` -> `这下看懂了` -> `此事已成`.
- Boast -> collapse: `此事已成` -> `悔恨了` -> `原来我是区`.
- Arrival -> loss: `{对象}到了` -> `{对象}倒了`.
- Artificial rule -> inversion: `{条件}算你输了` -> `条件发生，算我输了`.
- Missing object -> payoff: `{对象}藏好了` -> `{对象}终于到了` -> `二审维持原判`.
- Saved resource -> commitment: `保护果汁` -> `留着过年吗` -> `这口终于喝对了`.
- Mock lesson -> retest: `记笔记` -> later matching scene -> `二审维持原判` or `撤回笔记`.

A callback may deliberately repeat its anchor. Change at least one noun, verb, verdict, or consequence so it lands as development rather than duplication.

## Anti-repetition controls

- Do not use any of `这下看懂了`, `吓哭了`, `老霸道了`, `悔恨了`, `关键起防`, or `气笑了` more than once in five resolved updates unless completing a callback.
- Do not use `我说` as the opening of consecutive updates.
- Do not use two recognition phrases from the same ladder stage in one sentence.
- Do not finish every update with a compressed verdict. Alternate question, declaration, mock report, comparison, personification, and callback endings.
- Do not force a famous phrase when a current noun can create a fresh mutation.
- Do not imitate raw danmaku errors blindly. Preserve intentional forms such as `何意味`, `不拿拿`, and meaningful sound-alikes; use readable Chinese elsewhere.
- Do not treat frequency as quality. The most frequent exact corpus phrases are anchors that require stronger cooldowns.

## Assembly examples

```text
自动化返能把第二轮接上了，核心牌终于不用在牌堆底下开会。我已启动；刚才说它游牧，现在老爸到了，二审维持原判。

这回合格挡差 1，血条得替防牌上一天班。精妙的数值设计，设计到我头上了；我说掉血算你输了——行，算我输了。

商店三件都对口，金币只够看不能够买。唯一三个老爸都来了，钱包先倒了；商人你玩不玩，贵确实有贵的道理。

药水再不喝就真要带进下一局了，这口保住 11 血。保护果汁终于结束文物生涯；刚才问留着过年吗，现在算它专业对口。

核心攻击连续两轮沉底，发牌员游牧了；敌人听说我们没有输出闻着味就来了。此事本来已成，现在晦涩难懂，我已平庸。

接口收了出牌请求却没推进状态，先不补第二次输入。动画卡我启动了，状态还在工地拧螺丝；东尼出来说话，这 UI 何意味。
```

The examples demonstrate composition and callback. Do not recycle them verbatim when the current cards, enemies, numbers, and consequences can be named.
