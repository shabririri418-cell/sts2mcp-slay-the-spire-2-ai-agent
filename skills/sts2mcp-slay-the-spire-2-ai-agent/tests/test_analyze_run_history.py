import sys
from pathlib import Path
import unittest


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import analyze_run_history


class RunHistoryAnalysisTests(unittest.TestCase):
    def test_structural_metrics_are_reconstructed_from_floor_deltas(self):
        run = {
            "win": False,
            "was_abandoned": False,
            "killed_by_encounter": "ENCOUNTER.TEST_BOSS",
            "ascension": 10,
            "seed": "TEST",
            "build_id": "v0.test",
            "players": [
                {
                    "id": 1,
                    "character": "CHARACTER.DEFECT",
                    "deck": [
                        {"id": "CARD.A"},
                        {"id": "CARD.B"},
                        {"id": "CARD.C"},
                        {"id": "CARD.D"},
                        {"id": "CARD.E"},
                    ],
                    "relics": [{"id": "RELIC.ONE"}, {"id": "RELIC.TWO"}],
                    "potions": [],
                }
            ],
            "map_point_history": [
                [
                    {
                        "map_point_type": "monster",
                        "rooms": [{"room_type": "monster", "model_id": "ENCOUNTER.ONE", "turns_taken": 3}],
                        "player_stats": [
                            {
                                "player_id": 1,
                                "current_hp": 50,
                                "max_hp": 60,
                                "damage_taken": 10,
                                "cards_gained": [{"id": "CARD.D"}],
                                "card_choices": [
                                    {"card": {"id": "CARD.D"}, "was_picked": True},
                                    {"card": {"id": "CARD.X"}, "was_picked": False},
                                ],
                                "potion_used": ["POTION.ONE"],
                            }
                        ],
                    }
                ],
                [
                    {
                        "map_point_type": "shop",
                        "rooms": [{"room_type": "shop"}],
                        "player_stats": [
                            {
                                "player_id": 1,
                                "current_hp": 50,
                                "max_hp": 60,
                                "cards_gained": [{"id": "CARD.E"}],
                                "cards_removed": [{"id": "CARD.STARTER"}],
                                "gold_spent": 100,
                            }
                        ],
                    },
                    {
                        "map_point_type": "rest_site",
                        "rooms": [{"room_type": "rest_site"}],
                        "player_stats": [
                            {
                                "player_id": 1,
                                "current_hp": 60,
                                "max_hp": 60,
                                "hp_healed": 10,
                                "rest_site_choices": ["HEAL"],
                            }
                        ],
                    },
                ],
                [
                    {
                        "map_point_type": "boss",
                        "rooms": [{"room_type": "boss", "model_id": "ENCOUNTER.TEST_BOSS", "turns_taken": 8}],
                        "player_stats": [
                            {
                                "player_id": 1,
                                "current_hp": 0,
                                "max_hp": 60,
                                "damage_taken": 60,
                                "cards_gained": [{"id": "CARD.F"}],
                                "cards_removed": [{"id": "CARD.F"}],
                                "potion_used": ["POTION.TWO", "POTION.THREE"],
                            }
                        ],
                    }
                ],
            ],
        }

        report = analyze_run_history.analyze_run(run)

        self.assertEqual(report["deck"]["inferred_starting_size"], 4)
        self.assertEqual(report["deck"]["size_at_act_end"], [5, 5, 5])
        self.assertEqual(report["rewards"]["combat_card_screens"], 1)
        self.assertEqual(report["rewards"]["cards_picked"], 1)
        self.assertEqual(report["resources"]["potions_used_total"], 3)
        self.assertEqual(report["resources"]["shop_removal_count"], 1)
        self.assertEqual(report["route"]["damage_by_act"], [10, 0, 60])


if __name__ == "__main__":
    unittest.main()
