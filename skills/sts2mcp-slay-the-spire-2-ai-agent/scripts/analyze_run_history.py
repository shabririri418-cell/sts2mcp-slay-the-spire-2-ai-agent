#!/usr/bin/env python3
"""Produce deterministic structural metrics from an STS2 .run history file."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


class RunHistoryError(ValueError):
    pass


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _card_id(card):
    if isinstance(card, dict):
        return card.get("id")
    return str(card) if card is not None else None


def _room(point):
    rooms = _as_list(point.get("rooms"))
    return rooms[0] if rooms else {}


def _player_stats(point, player_id):
    stats = _as_list(point.get("player_stats"))
    if not stats:
        return {}
    if player_id is None:
        return stats[0]
    for item in stats:
        if item.get("player_id") == player_id:
            return item
    return {}


def _select_player(run, player_id):
    players = _as_list(run.get("players"))
    if not players:
        raise RunHistoryError("run history has no players")
    if player_id is None:
        return players[0]
    for player in players:
        if player.get("id") == player_id:
            return player
    raise RunHistoryError("player id {} was not found".format(player_id))


def _choice_ids(choices):
    result = []
    for choice in _as_list(choices):
        if isinstance(choice, dict):
            result.append(choice.get("choice") or _card_id(choice.get("card")))
        else:
            result.append(str(choice))
    return [item for item in result if item]


def analyze_run(run, player_id=None):
    if not isinstance(run, dict):
        raise RunHistoryError("run history must be a JSON object")

    player = _select_player(run, player_id)
    selected_player_id = player.get("id")
    acts = _as_list(run.get("map_point_history"))
    if not acts:
        raise RunHistoryError("run history has no map_point_history")

    floor_rows = []
    floor_number = 0
    map_counts = Counter()
    combat_counts = Counter()
    act_damage = []
    combat_rewards = []
    removal_events = []
    upgrade_events = []
    rest_events = []
    shop_events = []
    difficult_fights = []
    potion_used_count = 0
    net_deltas_by_act = []

    for act_index, act_points in enumerate(acts, start=1):
        damage_this_act = 0
        net_delta_this_act = 0
        for point in _as_list(act_points):
            floor_number += 1
            stats = _player_stats(point, selected_player_id)
            room = _room(point)
            room_type = room.get("room_type") or "unknown"
            map_type = point.get("map_point_type") or "unknown"
            map_counts[map_type] += 1
            if room_type in ("monster", "elite", "boss"):
                combat_counts[room_type] += 1

            damage = int(stats.get("damage_taken") or 0)
            damage_this_act += damage
            gained = _as_list(stats.get("cards_gained"))
            removed = _as_list(stats.get("cards_removed"))
            upgrades = _as_list(stats.get("upgraded_cards"))
            net_delta = len(gained) - len(removed)
            net_delta_this_act += net_delta

            used_potions = _as_list(stats.get("potion_used"))
            potion_used_count += len(used_potions)
            if removed:
                removal_events.append(
                    {
                        "floor": floor_number,
                        "room_type": room_type,
                        "cards": [_card_id(card) for card in removed],
                    }
                )
            if upgrades:
                upgrade_events.append(
                    {
                        "floor": floor_number,
                        "room_type": room_type,
                        "cards": [_card_id(card) for card in upgrades],
                    }
                )

            rest_choices = _as_list(stats.get("rest_site_choices"))
            if rest_choices:
                rest_events.append(
                    {
                        "floor": floor_number,
                        "choices": rest_choices,
                        "hp_after": stats.get("current_hp"),
                        "max_hp": stats.get("max_hp"),
                        "hp_healed": int(stats.get("hp_healed") or 0),
                        "potions_offered": _choice_ids(stats.get("potion_choices")),
                    }
                )

            if room_type == "shop":
                shop_events.append(
                    {
                        "floor": floor_number,
                        "gold_spent": int(stats.get("gold_spent") or 0),
                        "cards_gained": [_card_id(card) for card in gained],
                        "cards_removed": [_card_id(card) for card in removed],
                        "relics_bought": _as_list(stats.get("bought_relics")),
                    }
                )

            card_choices = _as_list(stats.get("card_choices"))
            if room_type in ("monster", "elite", "boss") and card_choices:
                picked = [
                    _card_id(choice.get("card"))
                    for choice in card_choices
                    if isinstance(choice, dict) and choice.get("was_picked") is True
                ]
                combat_rewards.append(
                    {
                        "floor": floor_number,
                        "room_type": room_type,
                        "picked": [card for card in picked if card],
                        "skipped": not bool(picked),
                    }
                )

            if room_type in ("elite", "boss"):
                difficult_fights.append(
                    {
                        "floor": floor_number,
                        "room_type": room_type,
                        "encounter": room.get("model_id"),
                        "turns": room.get("turns_taken"),
                        "damage_taken": damage,
                        "hp_after": stats.get("current_hp"),
                        "potions_used": used_potions,
                    }
                )

            floor_rows.append(
                {
                    "floor": floor_number,
                    "act": act_index,
                    "map_type": map_type,
                    "room_type": room_type,
                    "encounter": room.get("model_id"),
                    "damage_taken": damage,
                    "hp_after": stats.get("current_hp"),
                    "cards_gained": [_card_id(card) for card in gained],
                    "cards_removed": [_card_id(card) for card in removed],
                    "potions_used": used_potions,
                    "net_deck_delta": net_delta,
                }
            )

        act_damage.append(damage_this_act)
        net_deltas_by_act.append(net_delta_this_act)

    final_deck = _as_list(player.get("deck"))
    final_deck_size = len(final_deck)
    total_net_delta = sum(net_deltas_by_act)
    inferred_starting_deck_size = final_deck_size - total_net_delta
    running_size = inferred_starting_deck_size
    deck_size_at_act_end = []
    for delta in net_deltas_by_act:
        running_size += delta
        deck_size_at_act_end.append(running_size)

    reward_picks = sum(1 for item in combat_rewards if not item["skipped"])
    reward_screens = len(combat_rewards)
    reward_pick_rate = reward_picks / reward_screens if reward_screens else None
    difficult_potion_count = sum(len(item["potions_used"]) for item in difficult_fights)
    difficult_count = len(difficult_fights)
    difficult_potion_rate = (
        difficult_potion_count / difficult_count if difficult_count else None
    )
    full_hp_rests = [
        event
        for event in rest_events
        if "HEAL" in event["choices"]
        and event["hp_healed"] == 0
        and event["hp_after"] == event["max_hp"]
    ]
    shop_removal_count = sum(len(event["cards_removed"]) for event in shop_events)

    observations = []
    if final_deck_size >= 35:
        observations.append("large_final_deck_review_consistency")
    if reward_pick_rate is not None and reward_pick_rate >= 0.9:
        observations.append("high_combat_reward_pick_rate")
    if len(shop_events) >= 4 and shop_removal_count <= 1:
        observations.append("low_shop_removal_frequency")
    if difficult_potion_rate is not None and difficult_potion_rate >= 1.5:
        observations.append("high_potion_use_in_elite_and_boss_fights")
    if full_hp_rests:
        observations.append("full_hp_rest_choices_require_upgrade_comparison")

    return {
        "run": {
            "win": run.get("win"),
            "was_abandoned": run.get("was_abandoned"),
            "killed_by_encounter": run.get("killed_by_encounter"),
            "killed_by_event": run.get("killed_by_event"),
            "ascension": run.get("ascension"),
            "seed": run.get("seed"),
            "build_id": run.get("build_id"),
            "character": player.get("character"),
            "player_id": selected_player_id,
        },
        "route": {
            "floors": floor_number,
            "map_counts": dict(sorted(map_counts.items())),
            "combat_counts": dict(sorted(combat_counts.items())),
            "damage_by_act": act_damage,
        },
        "deck": {
            "inferred_starting_size": inferred_starting_deck_size,
            "size_at_act_end": deck_size_at_act_end,
            "final_size": final_deck_size,
            "net_delta_by_act": net_deltas_by_act,
            "final_cards": [
                {
                    "id": _card_id(card),
                    "upgrade": card.get("current_upgrade_level", 0)
                    if isinstance(card, dict)
                    else 0,
                    "floor_added": card.get("floor_added_to_deck")
                    if isinstance(card, dict)
                    else None,
                }
                for card in final_deck
            ],
            "removal_events": removal_events,
            "upgrade_events": upgrade_events,
        },
        "rewards": {
            "combat_card_screens": reward_screens,
            "cards_picked": reward_picks,
            "cards_skipped": reward_screens - reward_picks,
            "pick_rate": reward_pick_rate,
            "events": combat_rewards,
        },
        "resources": {
            "final_relics": len(_as_list(player.get("relics"))),
            "final_potions": len(_as_list(player.get("potions"))),
            "potions_used_total": potion_used_count,
            "potions_used_in_elites_and_bosses": difficult_potion_count,
            "potions_per_elite_or_boss": difficult_potion_rate,
            "rest_choices": rest_events,
            "full_hp_rest_count": len(full_hp_rests),
            "shops": shop_events,
            "shop_removal_count": shop_removal_count,
        },
        "difficult_fights": difficult_fights,
        "observations": observations,
        "floors": floor_rows,
    }


def _resolve_run_path(value):
    path = Path(value).expanduser()
    if path.is_dir():
        candidates = sorted(path.glob("*.run"), key=lambda item: item.stat().st_mtime)
        if not candidates:
            raise RunHistoryError("no .run files found in {}".format(path))
        return candidates[-1]
    if not path.is_file():
        raise RunHistoryError("run history file not found: {}".format(path))
    return path


def _load_run(path):
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def _text_summary(report):
    run = report["run"]
    deck = report["deck"]
    rewards = report["rewards"]
    resources = report["resources"]
    route = report["route"]
    lines = [
        "seed={} build={} ascension={} win={} killed_by={}".format(
            run.get("seed"),
            run.get("build_id"),
            run.get("ascension"),
            run.get("win"),
            run.get("killed_by_encounter") or run.get("killed_by_event"),
        ),
        "deck: start={} act_end={} final={}".format(
            deck["inferred_starting_size"],
            ",".join(str(value) for value in deck["size_at_act_end"]),
            deck["final_size"],
        ),
        "combat rewards: picked={}/{} skipped={}".format(
            rewards["cards_picked"],
            rewards["combat_card_screens"],
            rewards["cards_skipped"],
        ),
        "route: floors={} damage_by_act={}".format(
            route["floors"], ",".join(str(value) for value in route["damage_by_act"])
        ),
        "resources: relics={} potions_used={} difficult_potions={} shop_removals={} full_hp_rests={}".format(
            resources["final_relics"],
            resources["potions_used_total"],
            resources["potions_used_in_elites_and_bosses"],
            resources["shop_removal_count"],
            resources["full_hp_rest_count"],
        ),
        "observations: {}".format(", ".join(report["observations"]) or "none"),
    ]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Analyze an STS2 .run history file.")
    parser.add_argument("input", help=".run file or directory containing .run files")
    parser.add_argument("--player-id", type=int)
    parser.add_argument("--format", choices=("json", "text"), default="json")
    parser.add_argument("--compact", action="store_true", help="emit compact JSON")
    args = parser.parse_args(argv)

    try:
        path = _resolve_run_path(args.input)
        report = analyze_run(_load_run(path), player_id=args.player_id)
    except (RunHistoryError, json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2

    if args.format == "text":
        print(_text_summary(report))
    else:
        print(
            json.dumps(
                report,
                ensure_ascii=False,
                indent=None if args.compact else 2,
                sort_keys=False,
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
