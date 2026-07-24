#!/usr/bin/env python3
"""Query the bundled WanWiki zh-CN snapshot without network access."""

import argparse
import copy
import json
import sqlite3
import sys
import time
from pathlib import Path


DATABASE = Path(__file__).resolve().parents[1] / "references" / "wanwiki_zh_cn.sqlite3"
DEFAULT_MAX_CHARS = 4800
FULL_MAX_CHARS = 20000
MAX_LIMIT = 20


def load_rows(connection, categories):
    sql = """
        SELECT category, entity_id, name, slug, aliases_json, summary,
               search_text, payload_json, source_url, snapshot_at
        FROM records
    """
    parameters = []
    if categories:
        placeholders = ",".join("?" for _ in categories)
        sql += " WHERE category IN ({})".format(placeholders)
        parameters.extend(categories)
    return connection.execute(sql, parameters).fetchall()


def normalize(value):
    return " ".join(str(value).casefold().split())


def score_row(row, terms, entity_id, match_any):
    category, row_id, name, slug, aliases_json, summary, search_text = row[:7]
    aliases = json.loads(aliases_json)
    normalized_id = normalize(row_id)
    normalized_name = normalize(name)
    normalized_slug = normalize(slug)
    normalized_aliases = [normalize(alias) for alias in aliases]
    haystack = normalize(" ".join([row_id, name, slug, summary, search_text] + aliases))

    if entity_id:
        wanted = normalize(entity_id)
        if wanted not in (normalized_id, normalized_slug) and wanted not in normalized_aliases:
            return None
        return 2000

    if not terms:
        return 1
    score = 0
    matched = 0
    for term in terms:
        if term == normalized_name:
            term_score = 1000
        elif term == normalized_id or term == normalized_slug:
            term_score = 950
        elif term in normalized_aliases:
            term_score = 900
        elif term in normalized_name:
            term_score = 650
        elif term in normalized_slug or term in normalized_id:
            term_score = 500
        elif term in normalize(summary):
            term_score = 240
        elif term in haystack:
            term_score = 100
        else:
            if match_any:
                continue
            return None
        score += term_score
        matched += 1
    if not matched:
        return None
    if category in ("cards", "relics", "potions", "statuses", "monsters", "events"):
        score += 10
    return score


def compact_payload(category, payload):
    data = copy.deepcopy(payload)
    data.pop("locale", None)
    if category == "monsters":
        data.pop("nodes", None)
        data.pop("edges", None)
        if isinstance(data.get("moveFlow"), dict):
            data["moveFlow"].pop("nodes", None)
            data["moveFlow"].pop("edges", None)
    elif category == "events":
        compact_pages = []
        for page in data.get("pages", []):
            item = {
                key: page[key]
                for key in (
                    "sourceKey",
                    "description",
                    "dynamicContextKinds",
                    "isInitial",
                )
                if key in page
            }
            options = []
            for option in page.get("options", []):
                options.append(
                    {
                        key: option[key]
                        for key in (
                            "sourceKey",
                            "title",
                            "description",
                            "dynamicContextKinds",
                            "nextPageSourceKeys",
                            "nextPageSourcePatterns",
                        )
                        if key in option
                    }
                )
            item["options"] = options
            compact_pages.append(item)
        if compact_pages:
            data["pages"] = compact_pages
    return data


def find_largest_reducible_list(value, path=()):
    best = None
    if isinstance(value, list) and len(value) > 1:
        best = (len(json.dumps(value, ensure_ascii=False)), path, value)
    if isinstance(value, dict):
        for key, nested in value.items():
            candidate = find_largest_reducible_list(nested, path + (str(key),))
            if candidate and (best is None or candidate[0] > best[0]):
                best = candidate
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            candidate = find_largest_reducible_list(nested, path + (str(index),))
            if candidate and (best is None or candidate[0] > best[0]):
                best = candidate
    return best


def fit_record(record, budget):
    fitted = copy.deepcopy(record)
    omitted = {}
    while len(json.dumps(fitted, ensure_ascii=False, separators=(",", ":"))) > budget:
        candidate = find_largest_reducible_list(fitted.get("data", {}))
        if candidate is None:
            fitted.pop("data", None)
            fitted["available_fields"] = sorted(record.get("data", {}).keys())
            fitted["detail_required"] = True
            break
        _, path, target = candidate
        target.pop()
        key = ".".join(path) or "data"
        omitted[key] = omitted.get(key, 0) + 1
    if omitted:
        fitted["truncated_paths"] = omitted
        fitted["detail_required"] = True
    return fitted


def record_from_row(row, full):
    (
        category,
        entity_id,
        name,
        slug,
        aliases_json,
        summary,
        _search_text,
        payload_json,
        source_url,
        snapshot_at,
    ) = row
    payload = json.loads(payload_json)
    if not full:
        payload = compact_payload(category, payload)
    result = {
        "category": category,
        "id": entity_id,
        "name": name,
        "slug": slug,
        "aliases": json.loads(aliases_json),
        "summary": summary,
        "data": payload,
        "source_url": source_url,
        "snapshot_at": snapshot_at,
    }
    if not full and category in ("monsters", "events"):
        result["full_detail_command"] = (
            "py -3 scripts/query_wanwiki.py --id {} --category {} --full".format(
                entity_id, category
            )
        )
    if not full and category == "monsters" and isinstance(payload.get("moveFlow"), dict):
        result["compact_omissions"] = ["moveFlow.nodes", "moveFlow.edges"]
    return result


def render_json(scored_rows, limit, max_chars, full, query_terms, elapsed_ms):
    base = {
        "offline": True,
        "query": query_terms,
        "result_count": 0,
        "results": [],
        "elapsed_ms": round(elapsed_ms, 3),
    }
    for _, row in scored_rows[:limit]:
        record = record_from_row(row, full)
        remaining = max_chars - len(
            json.dumps(base, ensure_ascii=False, separators=(",", ":"))
        ) - 32
        record = fit_record(record, max(400, remaining))
        candidate = copy.deepcopy(base)
        candidate["results"].append(record)
        candidate["result_count"] = len(candidate["results"])
        encoded = json.dumps(candidate, ensure_ascii=False, separators=(",", ":"))
        if len(encoded) <= max_chars:
            base = candidate
        else:
            break
    base["result_count"] = len(base["results"])
    base["more_matches"] = max(0, min(limit, len(scored_rows)) - len(base["results"]))
    return json.dumps(base, ensure_ascii=False, separators=(",", ":"))


def render_text(scored_rows, limit, max_chars, full, query_terms, elapsed_ms):
    lines = [
        "offline: true",
        "query: {}".format(" | ".join(query_terms) if query_terms else "<all>"),
        "elapsed_ms: {:.3f}".format(elapsed_ms),
    ]
    for _, row in scored_rows[:limit]:
        record = record_from_row(row, full)
        block = "\n---\n" + json.dumps(record, ensure_ascii=False, indent=2)
        if len("\n".join(lines)) + len(block) > max_chars:
            remaining = max_chars - len("\n".join(lines)) - 10
            record = fit_record(record, max(400, remaining))
            block = "\n---\n" + json.dumps(record, ensure_ascii=False, indent=2)
        if len("\n".join(lines)) + len(block) > max_chars:
            break
        lines.append(block)
    return "\n".join(lines)


def print_stats(connection):
    meta = dict(connection.execute("SELECT key, value FROM meta ORDER BY key"))
    counts = dict(
        connection.execute(
            "SELECT category, COUNT(*) FROM records GROUP BY category ORDER BY category"
        )
    )
    output = {"offline": True, "meta": meta, "counts": counts}
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Query the bundled offline WanWiki zh-CN snapshot."
    )
    parser.add_argument("query", nargs="*", help="Names, IDs, aliases, or mechanics")
    parser.add_argument("--id", help="Exact entity ID, slug, or alias")
    parser.add_argument(
        "--category",
        action="append",
        help="Restrict category; repeat or comma-separate values",
    )
    parser.add_argument(
        "--character",
        help="Restrict cards/relics to a character or owner ID",
    )
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--max-chars", type=int)
    parser.add_argument("--full", action="store_true", help="Return full stored payload")
    parser.add_argument(
        "--any",
        action="store_true",
        help="Match any query term; useful for batching several entity names",
    )
    parser.add_argument("--format", choices=("json", "text"), default="json")
    parser.add_argument("--stats", action="store_true")
    args = parser.parse_args()

    if not DATABASE.exists():
        parser.error("offline database is missing: {}".format(DATABASE))
    if args.limit < 1 or args.limit > MAX_LIMIT:
        parser.error("--limit must be between 1 and {}".format(MAX_LIMIT))
    max_chars = args.max_chars or (FULL_MAX_CHARS if args.full else DEFAULT_MAX_CHARS)
    if max_chars < 800 or max_chars > 100000:
        parser.error("--max-chars must be between 800 and 100000")
    categories = []
    for group in args.category or []:
        categories.extend(item.strip() for item in group.split(",") if item.strip())
    terms = [normalize(term) for term in args.query if normalize(term)]

    started = time.perf_counter()
    connection = sqlite3.connect("file:{}?mode=ro".format(DATABASE.as_posix()), uri=True)
    try:
        if args.stats:
            print_stats(connection)
            return
        rows = load_rows(connection, categories)
    finally:
        connection.close()

    scored = []
    for row in rows:
        if args.character:
            payload = json.loads(row[7])
            owner = payload.get("characterId") or payload.get("ownerId")
            if normalize(owner or "") != normalize(args.character):
                continue
        score = score_row(row, terms, args.id, args.any)
        if score is not None:
            scored.append((score, row))
    scored.sort(key=lambda item: (-item[0], item[1][0], item[1][2]))
    elapsed_ms = (time.perf_counter() - started) * 1000
    display_query = list(args.query)
    if args.id:
        display_query.append("id={}".format(args.id))
    if args.format == "json":
        output = render_json(
            scored, args.limit, max_chars, args.full, display_query, elapsed_ms
        )
    else:
        output = render_text(
            scored, args.limit, max_chars, args.full, display_query, elapsed_ms
        )
    print(output)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(0)
