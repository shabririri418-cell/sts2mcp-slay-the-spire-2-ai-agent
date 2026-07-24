# WanWiki zh-CN offline knowledge

## Scope

- Snapshot time: `2026-07-24T18:33:20+00:00` (`2026-07-25 02:33:20` Asia/Shanghai).
- Source: `https://spire2.wanwiki.com/zh-CN` and its public HTML collection pages.
- Sitemap contained 125 `zh-CN` URLs at snapshot time.
- The snapshot stores structured game facts and mechanics, not raw HTML, images, site UI, or article mirrors.
- `/api/` and `/_next/` were not fetched because `robots.txt` disallows them.
- Source content signals permitted reference use and prohibited AI training. Site terms prohibited whole-site mirroring and abusive crawling. The build used low-rate requests to public HTML only.

## Stored coverage

| Category | Records |
|---|---:|
| Cards | 577 |
| Relics | 296 |
| Potions | 63 |
| Statuses | 311 |
| Enchantments | 22 |
| Characters | 5 |
| Acts | 4 |
| Monsters | 101 |
| Events | 57 |
| Glossary entries and aliases | 267 |

The home page displayed 100 monsters while the structured bestiary payload contained 101 records. Preserve all 101 and treat the difference as a source inconsistency rather than silently deleting one.

## Runtime contract

- Never access WanWiki or another online knowledge source while controlling a game.
- Query `references/wanwiki_zh_cn.sqlite3` only through `scripts/query_wanwiki.py`.
- Treat the live STS2MCP state and game text as authoritative. Treat this snapshot as version-sensitive reference evidence.
- If the game build is newer than the snapshot or conflicts with it, continue offline, prefer live data, and label the snapshot result stale or uncertain.
- Do not preload the database into context. Query only relevant entities and reuse unchanged results during the run.

## Query examples

```powershell
py -3 <skill-path>\scripts\query_wanwiki.py 痛击 --category cards --limit 1
py -3 <skill-path>\scripts\query_wanwiki.py 痛击 防御 打击 --any --category cards --character ironclad --limit 3
py -3 <skill-path>\scripts\query_wanwiki.py 易伤 --category statuses --limit 4
py -3 <skill-path>\scripts\query_wanwiki.py --id waterfall-giant --category monsters
```

Default output is compact and capped at 4,800 characters. Compact monster results include every listed move but omit the detailed move-flow nodes and edges. Rerun the exact entity with `--full` when move ordering or branching matters, or whenever a result reports `detail_required: true`; do not guess from omitted or truncated branches.

```powershell
py -3 <skill-path>\scripts\query_wanwiki.py --id waterfall-giant --category monsters --full
```

Use `--stats` to inspect snapshot metadata and category counts. The query script contains no networking code.
