#!/usr/bin/env python3
"""Local queue, synthesis, and playback worker for personal Mambo narration."""

from collections import deque
import audioop
from dataclasses import dataclass
import io
import json
import os
from pathlib import Path
import re
import socketserver
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request
import wave
import winsound


HOST = "127.0.0.1"
PORT = 15527
ENGINE_HOST = "127.0.0.1"
ENGINE_PORT = 9880
SERVICE = "sts2-mambo-narrator"
VOICE = "曼波"
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
RUNTIME_DIR = SKILL_DIR / ".runtime" / "MamboTTS-v1.1.0" / "MamboTTS_Full"
ENGINE_DIR = RUNTIME_DIR / "GPT-SoVITS"
MODELS_DIR = RUNTIME_DIR / "models"
ENGINE_PYTHON = ENGINE_DIR / "runtime" / "python.exe"
ENGINE_API = ENGINE_DIR / "api.py"
SOVITS_MODEL = MODELS_DIR / "mambo_e8_s352.pth"
GPT_MODEL = MODELS_DIR / "mambo-e15.ckpt"
REFERENCE_AUDIO = MODELS_DIR / "refer.wav"
REFERENCE_TEXT = "最近看大家都在讲自己的经历，球波也是忍不住了。"
PERSONAL_USE_FILE = SKILL_DIR / ".runtime" / "personal-use.json"
LOG_FILE = SKILL_DIR / ".runtime" / "tts-engine.log"
AUDIO_DIR = SKILL_DIR / ".runtime" / "audio"
MIN_CLAUSE_CHARS = 15
MAX_CLAUSE_CHARS = 35
MAX_READY_AUDIO = 1
SPLIT_PUNCTUATION = frozenset("，。？！；：,.?!;:")


@dataclass(frozen=True)
class Clause:
    priority: str
    text: str
    generation: int
    message_id: int
    index: int
    count: int


def validate_personal_use():
    policy = json.loads(PERSONAL_USE_FILE.read_text(encoding="utf-8"))
    if policy.get("scope") != "personal_noncommercial" or not policy.get("acknowledged"):
        raise RuntimeError("The local runtime is not acknowledged for personal noncommercial use")


def compatible_engine_online():
    try:
        with urllib.request.urlopen(
            "http://%s:%d/openapi.json" % (ENGINE_HOST, ENGINE_PORT), timeout=2.0
        ) as response:
            document = json.loads(response.read().decode("utf-8"))
    except (OSError, ValueError, urllib.error.URLError):
        return False
    paths = document.get("paths", {}) if isinstance(document, dict) else {}
    return "/set_model" in paths and "/control" in paths and "/" in paths


def normalize_text(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"!\[([^]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(?m)^\s{0,3}(?:#{1,6}|[-*+]|\d+\.)\s+", "", text)
    text = text.replace("**", "").replace("__", "").replace("~~", "")
    substitutions = {
        "HP": "血量",
        "API": "接口",
        "MCP": "M C P",
        "TTS": "语音合成",
        "SL": "读档",
    }
    for source, target in substitutions.items():
        text = text.replace(source, target)
    return re.sub(r"\s+", " ", text).strip()


def split_narration(text, min_chars=MIN_CLAUSE_CHARS, max_chars=MAX_CLAUSE_CHARS):
    """Split exact narration text into promptly playable, punctuation-aware clauses."""
    if min_chars < 1 or max_chars < min_chars:
        raise ValueError("invalid narration clause bounds")
    if len(text) <= max_chars:
        return [text]

    boundaries = [index + 1 for index, char in enumerate(text) if char in SPLIT_PUNCTUATION]
    clauses = []
    start = 0
    while start < len(text):
        remaining = len(text) - start
        if remaining <= max_chars:
            end = len(text)
        else:
            preferred = [
                boundary
                for boundary in boundaries
                if start + min_chars <= boundary <= start + max_chars
            ]
            end = preferred[0] if preferred else start + max_chars
        clause = text[start:end].strip()
        if clause:
            clauses.append(clause)
        start = end
        while start < len(text) and text[start].isspace():
            start += 1
    return clauses


class Narrator:
    def __init__(self):
        validate_personal_use()
        AUDIO_DIR.mkdir(parents=True, exist_ok=True)
        self.condition = threading.Condition()
        self.queue = deque()
        self.ready_queue = deque()
        self.synthesizing = None
        self.next_message_id = 0
        self.engine_process = None
        self.engine_owned = False
        self.engine_ready = False
        self.engine_starting = True
        self.playing = False
        self.current_priority = None
        self.current_clause = None
        self.last_error = None
        self.last_audio_bytes = 0
        self.last_peak_amplitude = 0
        self.completed_count = 0
        self.completed_clause_count = 0
        self.superseded_routine_count = 0
        self.last_completed_at = None
        self.generation = 0
        self.closed = False
        self.engine_thread = threading.Thread(target=self._start_engine, daemon=True)
        self.synthesis_thread = threading.Thread(target=self._synthesis_loop, daemon=True)
        self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.engine_thread.start()
        self.synthesis_thread.start()
        self.playback_thread.start()

    def _start_engine(self):
        try:
            if compatible_engine_online():
                raise RuntimeError(
                    "Port 9880 already hosts an unverified GPT-SoVITS instance; "
                    "refusing to assume that it uses the fixed Mambo model"
                )

            required = (ENGINE_PYTHON, ENGINE_API, SOVITS_MODEL, GPT_MODEL, REFERENCE_AUDIO)
            missing = [str(path) for path in required if not path.is_file()]
            if missing:
                raise RuntimeError("Missing engine files: %s" % ", ".join(missing))

            command = [
                str(ENGINE_PYTHON),
                str(ENGINE_API),
                "-a",
                ENGINE_HOST,
                "-p",
                str(ENGINE_PORT),
                "-s",
                str(SOVITS_MODEL),
                "-g",
                str(GPT_MODEL),
                "-dr",
                str(REFERENCE_AUDIO),
                "-dt",
                REFERENCE_TEXT,
                "-dl",
                "zh",
            ]
            creationflags = 0x08000000 if os.name == "nt" else 0
            environment = os.environ.copy()
            environment["PYTHONIOENCODING"] = "utf-8"
            environment["PYTHONUTF8"] = "1"
            log = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
            try:
                self.engine_process = subprocess.Popen(
                    command,
                    cwd=str(ENGINE_DIR),
                    stdin=subprocess.DEVNULL,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    creationflags=creationflags,
                    env=environment,
                )
            finally:
                log.close()
            self.engine_owned = True
            deadline = time.monotonic() + 150.0
            while time.monotonic() < deadline and not self.closed:
                if self.engine_process.poll() is not None:
                    raise RuntimeError(
                        "GPT-SoVITS exited during startup with code %s; see %s"
                        % (self.engine_process.returncode, LOG_FILE)
                    )
                if compatible_engine_online():
                    self.engine_ready = True
                    self.engine_starting = False
                    with self.condition:
                        self.condition.notify_all()
                    return
                time.sleep(0.5)
            raise RuntimeError("GPT-SoVITS did not become ready within 150 seconds")
        except Exception as error:
            self.last_error = str(error)
            self.engine_starting = False
            with self.condition:
                self.condition.notify_all()

    def enqueue(self, text, priority):
        clean = normalize_text(text)
        if not clean:
            raise ValueError("Narration text became empty after normalization")
        texts = split_narration(clean)
        stale_paths = []
        with self.condition:
            stale_paths, superseded = self._discard_pending_routines_locked()
            self.superseded_routine_count += superseded
            self.next_message_id += 1
            message_id = self.next_message_id
            clauses = [
                Clause(priority, clause, self.generation, message_id, index, len(texts))
                for index, clause in enumerate(texts, start=1)
            ]
            self.queue.extend(clauses)
            position = len(
                {
                    item.message_id
                    for item in list(self.queue)
                    + [ready[0] for ready in self.ready_queue]
                }
            )
            self.condition.notify_all()
        for path in stale_paths:
            self._delete_audio(path)
        return {
            "ok": True,
            "queued": True,
            "priority": priority,
            "position": position,
            "clauses": len(clauses),
        }

    def _discard_pending_routines_locked(self):
        stale_message_ids = {
            clause.message_id for clause in self.queue if clause.priority == "routine"
        }
        self.queue = deque(clause for clause in self.queue if clause.priority != "routine")

        kept_audio = deque()
        stale_paths = []
        for clause, path in self.ready_queue:
            if clause.priority == "routine":
                stale_message_ids.add(clause.message_id)
                stale_paths.append(path)
            else:
                kept_audio.append((clause, path))
        self.ready_queue = kept_audio

        if self.synthesizing and self.synthesizing.priority == "routine":
            stale_message_ids.add(self.synthesizing.message_id)
        return stale_paths, len(stale_message_ids)

    @staticmethod
    def _delete_audio(path):
        try:
            os.unlink(path)
        except OSError:
            pass

    def clear(self):
        stale_paths = []
        with self.condition:
            self.queue.clear()
            stale_paths = [path for _, path in self.ready_queue]
            self.ready_queue.clear()
            self.generation += 1
            self.condition.notify_all()
        for path in stale_paths:
            self._delete_audio(path)
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except RuntimeError:
            pass
        return {"ok": True, "cleared": True, "service": SERVICE}

    def _synthesize(self, text):
        payload = json.dumps(
            {
                "text": text,
                "text_language": "zh",
                "speed": 1.08,
                "cut_punc": "，。？！；",
            },
            ensure_ascii=False,
        ).encode("utf-8")
        request = urllib.request.Request(
            "http://%s:%d/" % (ENGINE_HOST, ENGINE_PORT),
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=120.0) as response:
            audio = response.read()
            media_type = response.headers.get("Content-Type", "")
        if len(audio) < 44 or "audio" not in media_type.lower():
            preview = audio[:300].decode("utf-8", errors="replace")
            raise RuntimeError("GPT-SoVITS returned invalid audio: %s" % preview)
        try:
            with wave.open(io.BytesIO(audio), "rb") as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                peak = audioop.max(frames, wav_file.getsampwidth())
        except (EOFError, wave.Error) as error:
            raise RuntimeError("GPT-SoVITS returned an invalid WAV file: %s" % error)
        if not frames or peak == 0:
            raise RuntimeError("GPT-SoVITS returned silent audio")
        self.last_audio_bytes = len(audio)
        self.last_peak_amplitude = peak
        handle, path = tempfile.mkstemp(prefix="sts2-mambo-", suffix=".wav", dir=str(AUDIO_DIR))
        with os.fdopen(handle, "wb") as output:
            output.write(audio)
        return path

    def _synthesis_loop(self):
        while True:
            with self.condition:
                while not self.closed and (
                    not self.queue
                    or not self.engine_ready
                    or len(self.ready_queue) >= MAX_READY_AUDIO
                ):
                    self.condition.wait(timeout=1.0)
                if self.closed:
                    return
                clause = self.queue.popleft()
                self.synthesizing = clause

            path = None
            try:
                path = self._synthesize(clause.text)
                with self.condition:
                    current = clause.generation == self.generation and not self.closed
                    newest_routine = not (
                        clause.priority == "routine"
                        and any(
                            item.priority == "routine"
                            and item.message_id != clause.message_id
                            for item in self.queue
                        )
                    )
                    if current and newest_routine:
                        self.ready_queue.append((clause, path))
                        path = None
                    self.last_error = None
            except Exception as error:
                self.last_error = "Narration failed: %s" % error
            finally:
                with self.condition:
                    self.synthesizing = None
                    self.condition.notify_all()
                if path:
                    self._delete_audio(path)

    def _playback_loop(self):
        while True:
            with self.condition:
                while not self.closed and not self.ready_queue:
                    self.condition.wait(timeout=1.0)
                if self.closed:
                    return
                clause, path = self.ready_queue.popleft()
                self.playing = True
                self.current_priority = clause.priority
                self.current_clause = "%d/%d" % (clause.index, clause.count)
                self.condition.notify_all()
            try:
                if clause.generation == self.generation and not self.closed:
                    winsound.PlaySound(path, winsound.SND_FILENAME)
                    self.completed_clause_count += 1
                    if clause.index == clause.count:
                        self.completed_count += 1
                        self.last_completed_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
                self.last_error = None
            except Exception as error:
                self.last_error = "Narration failed: %s" % error
            finally:
                with self.condition:
                    self.playing = False
                    self.current_priority = None
                    self.current_clause = None
                    self.condition.notify_all()
                self._delete_audio(path)

    def status(self):
        with self.condition:
            pending_clauses = list(self.queue) + [item[0] for item in self.ready_queue]
            if self.synthesizing:
                pending_clauses.append(self.synthesizing)
            routine_pending = len(
                {item.message_id for item in pending_clauses if item.priority == "routine"}
            )
            pivotal_pending = len(
                {item.message_id for item in pending_clauses if item.priority == "pivotal"}
            )
        return {
            "ok": self.last_error is None,
            "service": SERVICE,
            "voice": VOICE,
            "configured": True,
            "running": self.engine_ready,
            "engine_ready": self.engine_ready,
            "engine_starting": self.engine_starting,
            "engine_pid": self.engine_process.pid if self.engine_process else None,
            "engine_owned": self.engine_owned,
            "playing": self.playing,
            "current_priority": self.current_priority,
            "current_clause": self.current_clause,
            "synthesizing": self.synthesizing is not None,
            "ready_audio": len(self.ready_queue),
            "routine_pending": routine_pending,
            "pivotal_pending": pivotal_pending,
            "last_error": self.last_error,
            "last_audio_bytes": self.last_audio_bytes,
            "last_peak_amplitude": self.last_peak_amplitude,
            "completed_count": self.completed_count,
            "completed_clause_count": self.completed_clause_count,
            "superseded_routine_count": self.superseded_routine_count,
            "last_completed_at": self.last_completed_at,
            "usage_scope": "personal_noncommercial",
            "publication_allowed": False,
        }

    def close(self):
        self.closed = True
        self.clear()
        with self.condition:
            self.condition.notify_all()
        if self.engine_owned and self.engine_process and self.engine_process.poll() is None:
            self.engine_process.terminate()
            try:
                self.engine_process.wait(timeout=10.0)
            except subprocess.TimeoutExpired:
                self.engine_process.kill()


class RequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            payload = json.loads(self.rfile.readline(65536).decode("utf-8"))
            command = payload.get("command")
            if command == "status":
                response = self.server.narrator.status()
            elif command == "speak":
                priority = payload.get("priority", "routine")
                if priority not in ("routine", "pivotal"):
                    raise ValueError("priority must be routine or pivotal")
                text = payload.get("text", "")
                if not isinstance(text, str) or not text.strip():
                    raise ValueError("text must be a non-empty string")
                response = self.server.narrator.enqueue(text, priority)
            elif command == "clear":
                response = self.server.narrator.clear()
            elif command == "shutdown":
                response = {"ok": True, "shutting_down": True, "service": SERVICE}
                threading.Thread(target=self.server.shutdown, daemon=True).start()
            else:
                raise ValueError("unknown command: %r" % command)
        except Exception as error:
            response = {"ok": False, "service": SERVICE, "error": str(error)}
        self.wfile.write((json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8"))


class NarrationServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    narrator = Narrator()
    with NarrationServer((HOST, PORT), RequestHandler) as server:
        server.narrator = narrator
        try:
            server.serve_forever(poll_interval=0.25)
        finally:
            narrator.close()


if __name__ == "__main__":
    main()
