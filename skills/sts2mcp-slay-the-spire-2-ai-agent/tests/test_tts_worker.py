import sys
from collections import deque
import os
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest import mock


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import tts_worker


class SplitNarrationTests(unittest.TestCase):
    def test_short_text_is_unchanged(self):
        self.assertEqual(tts_worker.split_narration("短句直接播放。"), ["短句直接播放。"])

    def test_long_text_uses_punctuation_and_stays_bounded(self):
        text = "这一回合先解决前排敌人，避免六点伤害落到血量上；随后补足格挡，再保留药水应对精英。"
        clauses = tts_worker.split_narration(text)

        self.assertEqual("".join(clauses), text)
        self.assertTrue(all(len(clause) <= tts_worker.MAX_CLAUSE_CHARS for clause in clauses))
        self.assertGreater(len(clauses), 1)

    def test_unpunctuated_text_is_hard_limited(self):
        text = "甲" * 80
        clauses = tts_worker.split_narration(text)

        self.assertEqual("".join(clauses), text)
        self.assertTrue(all(len(clause) <= tts_worker.MAX_CLAUSE_CHARS for clause in clauses))


class QueuePolicyTests(unittest.TestCase):
    def make_narrator(self):
        narrator = tts_worker.Narrator.__new__(tts_worker.Narrator)
        narrator.condition = threading.Condition()
        narrator.queue = deque()
        narrator.ready_queue = deque()
        narrator.synthesizing = None
        narrator.next_message_id = 0
        narrator.generation = 0
        narrator.superseded_routine_count = 0
        narrator.engine_ready = True
        narrator.closed = False
        narrator.playing = False
        narrator.current_priority = None
        narrator.current_clause = None
        narrator.last_error = None
        narrator.completed_count = 0
        narrator.completed_clause_count = 0
        narrator.last_completed_at = None
        return narrator

    def test_only_latest_routine_remains_pending(self):
        narrator = self.make_narrator()
        narrator.enqueue("第一条例行解说，会被更新状态替代。", "routine")
        narrator.enqueue("第二条例行解说，是当前最新状态。", "routine")

        message_ids = {clause.message_id for clause in narrator.queue}
        self.assertEqual(message_ids, {2})
        self.assertEqual(narrator.superseded_routine_count, 1)

    def test_same_message_clauses_do_not_supersede_each_other(self):
        narrator = self.make_narrator()
        narrator.enqueue("甲" * 80, "routine")
        first = narrator.queue.popleft()

        newer_routine_exists = any(
            clause.priority == "routine" and clause.message_id != first.message_id
            for clause in narrator.queue
        )
        self.assertFalse(newer_routine_exists)
        self.assertGreater(len(narrator.queue), 0)

    def test_pivotal_clears_routine_but_preserves_pivotal_order(self):
        narrator = self.make_narrator()
        narrator.enqueue("第一条关键解说，必须完整保留。", "pivotal")
        narrator.enqueue("这条例行解说即将过时。", "routine")
        narrator.enqueue("第二条关键解说，也必须完整保留。", "pivotal")

        priorities = [clause.priority for clause in narrator.queue]
        message_ids = []
        for clause in narrator.queue:
            if not message_ids or message_ids[-1] != clause.message_id:
                message_ids.append(clause.message_id)
        self.assertEqual(set(priorities), {"pivotal"})
        self.assertEqual(message_ids, [1, 3])

    def test_synthesis_runs_ahead_of_current_playback(self):
        narrator = self.make_narrator()
        second_synthesis_started = threading.Event()
        overlap_observed = []
        synth_count = 0

        def fake_synthesize(_text):
            nonlocal synth_count
            synth_count += 1
            if synth_count == 2:
                second_synthesis_started.set()
            handle, path = tempfile.mkstemp(suffix=".wav")
            os.close(handle)
            return path

        def fake_play(_path, _flags):
            if not overlap_observed:
                overlap_observed.append(second_synthesis_started.wait(timeout=2.0))

        narrator._synthesize = fake_synthesize
        synthesis_thread = threading.Thread(target=narrator._synthesis_loop)
        playback_thread = threading.Thread(target=narrator._playback_loop)
        synthesis_thread.start()
        playback_thread.start()
        try:
            with mock.patch.object(tts_worker.winsound, "PlaySound", side_effect=fake_play):
                narrator.enqueue("甲" * 80, "pivotal")
                deadline = time.monotonic() + 3.0
                while narrator.completed_count < 1 and time.monotonic() < deadline:
                    time.sleep(0.01)
        finally:
            with narrator.condition:
                narrator.closed = True
                narrator.condition.notify_all()
            synthesis_thread.join(timeout=2.0)
            playback_thread.join(timeout=2.0)

        self.assertEqual(narrator.completed_count, 1)
        self.assertEqual(overlap_observed, [True])


if __name__ == "__main__":
    unittest.main()
