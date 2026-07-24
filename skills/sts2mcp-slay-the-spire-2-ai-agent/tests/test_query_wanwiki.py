import ast
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_DIR / "scripts" / "query_wanwiki.py"
DATABASE = SKILL_DIR / "references" / "wanwiki_zh_cn.sqlite3"


def run_query(*arguments):
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    completed = subprocess.run(
        [sys.executable, str(SCRIPT)] + list(arguments),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
    )
    return completed.stdout.strip(), json.loads(completed.stdout)


class OfflineWanWikiTests(unittest.TestCase):
    def test_runtime_script_has_no_network_imports(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        self.assertTrue({"urllib", "requests", "httpx", "socket"}.isdisjoint(imported))

    def test_database_exists(self):
        self.assertTrue(DATABASE.is_file())
        self.assertGreater(DATABASE.stat().st_size, 100_000)

    def test_exact_card_includes_base_and_upgrade_values(self):
        _, result = run_query("痛击", "--category", "cards", "--limit", "1")
        self.assertTrue(result["offline"])
        card = result["results"][0]
        self.assertEqual(card["id"], "bash")
        self.assertEqual(card["data"]["textVariables"]["Damage"], "8")
        self.assertEqual(card["data"]["upgradedTextVariables"]["Damage"], "10")

    def test_batch_card_lookup_respects_character(self):
        _, result = run_query(
            "痛击",
            "防御",
            "打击",
            "--any",
            "--category",
            "cards",
            "--character",
            "ironclad",
            "--limit",
            "3",
        )
        self.assertEqual({item["name"] for item in result["results"]}, {"痛击", "防御", "打击"})
        self.assertTrue(
            all(item["data"]["characterId"] == "ironclad" for item in result["results"])
        )

    def test_compact_monster_keeps_all_moves_within_budget(self):
        output, result = run_query(
            "--id",
            "waterfall-giant",
            "--category",
            "monsters",
            "--limit",
            "1",
            "--max-chars",
            "4800",
        )
        monster = result["results"][0]
        self.assertLessEqual(len(output), 4800)
        self.assertEqual(monster["data"]["moveCount"], 7)
        self.assertEqual(len(monster["data"]["moves"]), 7)
        self.assertEqual(monster["compact_omissions"], ["moveFlow.nodes", "moveFlow.edges"])

    def test_full_monster_restores_move_flow(self):
        _, result = run_query(
            "--id",
            "waterfall-giant",
            "--category",
            "monsters",
            "--limit",
            "1",
            "--full",
        )
        flow = result["results"][0]["data"]["moveFlow"]
        self.assertIn("nodes", flow)
        self.assertIn("edges", flow)

    def test_unknown_query_returns_no_results(self):
        _, result = run_query("绝对不存在的条目名")
        self.assertEqual(result["result_count"], 0)


if __name__ == "__main__":
    unittest.main()
