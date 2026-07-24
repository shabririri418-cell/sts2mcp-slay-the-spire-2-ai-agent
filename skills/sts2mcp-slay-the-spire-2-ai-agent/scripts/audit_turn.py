#!/usr/bin/env python3
"""Conservatively audit ordered end-of-turn damage packets.

The caller must normalize live STS2 state into explicit damage packets. This
tool performs deterministic arithmetic and fails closed when an effect is
unknown; it does not guess game rules that are absent from the input.
"""

import argparse
import json
import sys
from copy import deepcopy


CATEGORIES = ("enemy", "status", "queued", "other")


class AuditInputError(ValueError):
    pass


def _nonnegative_int(value, field):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AuditInputError("{} must be a non-negative integer".format(field))
    return value


def _normalize_packet(packet, index, default_category="other", default_order=None):
    if not isinstance(packet, dict):
        raise AuditInputError("damage_packets[{}] must be an object".format(index))

    source = str(packet.get("source") or "packet_{}".format(index))
    category = str(packet.get("category") or default_category)
    if category not in CATEGORIES:
        category = "other"

    damage = _nonnegative_int(packet.get("damage"), "{}.damage".format(source))
    hits = _nonnegative_int(packet.get("hits", 1), "{}.hits".format(source))
    order = _nonnegative_int(
        packet.get("order", index if default_order is None else default_order),
        "{}.order".format(source),
    )
    if hits == 0:
        raise AuditInputError("{}.hits must be greater than zero".format(source))

    return {
        "source": source,
        "category": category,
        "damage": damage,
        "hits": hits,
        "order": order,
        "known": packet.get("known", True) is True,
    }


def _counter_packets(triggers, unknown_effects, default_order_start):
    packets = []
    pending_sources = []
    for index, trigger in enumerate(triggers):
        if not isinstance(trigger, dict):
            unknown_effects.append("pending_counter_triggers[{}] is not an object".format(index))
            continue

        source = str(trigger.get("source") or "counter_trigger_{}".format(index))
        counter = trigger.get("counter")
        if isinstance(counter, bool) or not isinstance(counter, int) or counter < 0:
            unknown_effects.append("{} has an unknown counter".format(source))
            continue
        if counter != 0:
            continue

        pending_sources.append(source)
        if "damage" not in trigger:
            unknown_effects.append("{} is ready but its damage is unknown".format(source))
            continue
        try:
            normalized = _normalize_packet(
                    trigger,
                    index,
                    default_category="queued",
                    default_order=default_order_start + index,
                )
            packets.append(normalized)
            if not normalized["known"]:
                unknown_effects.append("{} is not fully known".format(source))
        except AuditInputError as exc:
            unknown_effects.append(str(exc))
    return packets, pending_sources


def audit_turn(data):
    """Return a fail-closed end-turn audit for a normalized input object."""
    if not isinstance(data, dict):
        raise AuditInputError("audit input must be a JSON object")

    player_hp = _nonnegative_int(data.get("player_hp"), "player_hp")
    current_block = _nonnegative_int(data.get("current_block", 0), "current_block")
    buffer_charges = _nonnegative_int(data.get("buffer_charges", 0), "buffer_charges")

    raw_unknown_effects = data.get("unknown_effects", [])
    if not isinstance(raw_unknown_effects, list):
        raise AuditInputError("unknown_effects must be an array")
    unknown_effects = [str(item) for item in raw_unknown_effects]
    raw_packets = data.get("damage_packets", [])
    raw_triggers = data.get("pending_counter_triggers", [])
    if not isinstance(raw_packets, list):
        raise AuditInputError("damage_packets must be an array")
    if not isinstance(raw_triggers, list):
        raise AuditInputError("pending_counter_triggers must be an array")

    packets = []
    for index, packet in enumerate(raw_packets):
        normalized = _normalize_packet(packet, index)
        packets.append(normalized)
        if not normalized["known"]:
            unknown_effects.append("{} is not fully known".format(normalized["source"]))

    trigger_packets, pending_sources = _counter_packets(
        raw_triggers, unknown_effects, len(raw_packets)
    )
    packets.extend(trigger_packets)
    packets.sort(key=lambda item: item["order"])

    category_totals = dict((category, 0) for category in CATEGORIES)
    remaining_block = current_block
    remaining_buffer = buffer_charges
    hp_damage = 0
    block_absorbed = 0
    buffer_spent = 0
    resolved_packets = []

    for packet in packets:
        category_totals[packet["category"]] += packet["damage"] * packet["hits"]
        packet_result = deepcopy(packet)
        packet_result["hit_results"] = []
        for _ in range(packet["hits"]):
            absorbed = min(remaining_block, packet["damage"])
            remaining_block -= absorbed
            block_absorbed += absorbed
            unblocked = packet["damage"] - absorbed
            prevented_by_buffer = False
            if unblocked > 0 and remaining_buffer > 0:
                remaining_buffer -= 1
                buffer_spent += 1
                unblocked = 0
                prevented_by_buffer = True
            hp_damage += unblocked
            packet_result["hit_results"].append(
                {
                    "block_absorbed": absorbed,
                    "buffer_spent": prevented_by_buffer,
                    "hp_damage": unblocked,
                }
            )
        resolved_packets.append(packet_result)

    known_damage_total = sum(category_totals.values())
    known_survival_margin = player_hp - hp_damage
    deduped_unknowns = list(dict.fromkeys(unknown_effects))
    worst_case_total = None if deduped_unknowns else known_damage_total
    survival_margin = None if deduped_unknowns else known_survival_margin
    safe_to_end_turn = not deduped_unknowns and known_survival_margin > 0

    return {
        "player_hp": player_hp,
        "current_block": current_block,
        "buffer_charges": buffer_charges,
        "visible_enemy_damage": category_totals["enemy"],
        "status_damage": category_totals["status"],
        "queued_damage": category_totals["queued"],
        "other_damage": category_totals["other"],
        "known_damage_total": known_damage_total,
        "worst_case_total": worst_case_total,
        "block_absorbed": block_absorbed,
        "block_remaining": remaining_block,
        "buffer_charges_spent": buffer_spent,
        "buffer_charges_remaining": remaining_buffer,
        "post_mitigation_damage": hp_damage,
        "known_survival_margin": known_survival_margin,
        "survival_margin": survival_margin,
        "pending_counter_triggers": pending_sources,
        "unknown_effects": deduped_unknowns,
        "safe_to_end_turn": safe_to_end_turn,
        "packets": resolved_packets,
    }


def _read_input(path):
    if path == "-":
        return json.load(sys.stdin)
    with open(path, "r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Audit a normalized STS2 end-turn damage ledger."
    )
    parser.add_argument("input", help="JSON file path, or - for standard input")
    parser.add_argument("--compact", action="store_true", help="emit compact JSON")
    args = parser.parse_args(argv)

    try:
        result = audit_turn(_read_input(args.input))
    except (AuditInputError, json.JSONDecodeError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=None if args.compact else 2,
            sort_keys=False,
        )
    )
    return 0 if result["safe_to_end_turn"] else 1


if __name__ == "__main__":
    sys.exit(main())
