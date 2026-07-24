import sys
import json
from pathlib import Path
import unittest


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SCRIPTS_DIR))

import audit_turn


class TurnAuditTests(unittest.TestCase):
    def test_aeonglass_delayed_fourth_withering_is_lethal(self):
        with (FIXTURES_DIR / "aeonglass_lethal.json").open(encoding="utf-8") as handle:
            result = audit_turn.audit_turn(json.load(handle))

        self.assertEqual(result["visible_enemy_damage"], 47)
        self.assertEqual(result["status_damage"], 36)
        self.assertEqual(result["queued_damage"], 12)
        self.assertEqual(result["worst_case_total"], 95)
        self.assertEqual(result["post_mitigation_damage"], 65)
        self.assertEqual(result["survival_margin"], -7)
        self.assertFalse(result["safe_to_end_turn"])

    def test_block_and_buffer_are_applied_in_hit_order(self):
        result = audit_turn.audit_turn(
            {
                "player_hp": 10,
                "current_block": 5,
                "buffer_charges": 1,
                "damage_packets": [
                    {"source": "small hit", "category": "enemy", "damage": 3},
                    {"source": "buffered hit", "category": "enemy", "damage": 10},
                    {"source": "last hit", "category": "enemy", "damage": 4},
                ],
            }
        )

        self.assertEqual(result["block_absorbed"], 5)
        self.assertEqual(result["buffer_charges_spent"], 1)
        self.assertEqual(result["post_mitigation_damage"], 4)
        self.assertEqual(result["survival_margin"], 6)
        self.assertTrue(result["safe_to_end_turn"])

    def test_ready_trigger_with_unknown_damage_fails_closed(self):
        result = audit_turn.audit_turn(
            {
                "player_hp": 80,
                "current_block": 80,
                "pending_counter_triggers": [
                    {"source": "unknown delayed effect", "counter": 0}
                ],
            }
        )

        self.assertFalse(result["safe_to_end_turn"])
        self.assertIsNone(result["worst_case_total"])
        self.assertIsNone(result["survival_margin"])
        self.assertIn(
            "unknown delayed effect is ready but its damage is unknown",
            result["unknown_effects"],
        )

    def test_exact_zero_hp_is_not_safe(self):
        result = audit_turn.audit_turn(
            {
                "player_hp": 5,
                "damage_packets": [
                    {"source": "exact lethal", "category": "enemy", "damage": 5}
                ],
            }
        )
        self.assertEqual(result["survival_margin"], 0)
        self.assertFalse(result["safe_to_end_turn"])


if __name__ == "__main__":
    unittest.main()
