#!/usr/bin/env python3
"""Control the local, personal-use-only Mambo narration worker."""

import argparse
import base64
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time


HOST = "127.0.0.1"
PORT = 15527
SERVICE = "sts2-mambo-narrator"
FIXED_VOICE = "曼波"
LEGACY_SERVICE = "sts2-kokoro-narrator"
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
RUNTIME_DIR = SKILL_DIR / ".runtime" / "MamboTTS-v1.1.0" / "MamboTTS_Full"
ENGINE_DIR = RUNTIME_DIR / "GPT-SoVITS"
PERSONAL_USE_FILE = SKILL_DIR / ".runtime" / "personal-use.json"
REQUIRED_FILES = (
    ENGINE_DIR / "runtime" / "python.exe",
    ENGINE_DIR / "api.py",
    RUNTIME_DIR / "models" / "mambo-e15.ckpt",
    RUNTIME_DIR / "models" / "mambo_e8_s352.pth",
    RUNTIME_DIR / "models" / "refer.wav",
    SCRIPT_DIR / "tts_worker.py",
)


def emit(value):
    print(json.dumps(value, ensure_ascii=True, separators=(",", ":")))


def request(payload, timeout=2.0):
    encoded = (json.dumps(payload, ensure_ascii=False) + "\n").encode("utf-8")
    with socket.create_connection((HOST, PORT), timeout=timeout) as connection:
        connection.sendall(encoded)
        connection.settimeout(timeout)
        chunks = []
        while True:
            chunk = connection.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
            if b"\n" in chunk:
                break
    if not chunks:
        raise RuntimeError("Narration worker returned an empty response")
    return json.loads(b"".join(chunks).split(b"\n", 1)[0].decode("utf-8"))


def worker_status():
    try:
        response = request({"command": "status"})
    except (OSError, ValueError, RuntimeError):
        return None
    return response if isinstance(response, dict) else None


def configuration_errors():
    errors = []
    try:
        policy = json.loads(PERSONAL_USE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        errors.append("personal-use acknowledgement is missing or invalid: %s" % error)
    else:
        if policy.get("scope") != "personal_noncommercial" or not policy.get("acknowledged"):
            errors.append("personal-use acknowledgement does not permit this local runtime")
    missing = [str(path) for path in REQUIRED_FILES if not path.is_file()]
    if missing:
        errors.append("missing runtime files: %s" % ", ".join(missing))
    return errors


def status():
    errors = configuration_errors()
    worker = worker_status()
    configured = not errors
    result = {
        "running": False,
        "service": SERVICE,
        "configured": configured,
        "voice": FIXED_VOICE,
        "usage_scope": "personal_noncommercial",
        "publication_allowed": False,
        "blocked": not configured,
    }
    if errors:
        result["reason"] = "; ".join(errors)
    if worker:
        result.update(worker)
        result["configured"] = configured
        result["running"] = bool(
            worker.get("service") == SERVICE and worker.get("engine_ready")
        )
        result["blocked"] = not configured
        if worker.get("service") == LEGACY_SERVICE:
            result["legacy_worker_running"] = True
    return result


def install():
    errors = configuration_errors()
    if errors:
        raise RuntimeError("Local runtime is incomplete. %s" % "; ".join(errors))
    emit(
        {
            "ok": True,
            "configured": True,
            "service": SERVICE,
            "voice": FIXED_VOICE,
            "usage_scope": "personal_noncommercial",
            "publication_allowed": False,
            "runtime": str(RUNTIME_DIR),
        }
    )


def start():
    errors = configuration_errors()
    if errors:
        raise RuntimeError("Cannot start narration. %s" % "; ".join(errors))
    existing = worker_status()
    if existing:
        if existing.get("service") != SERVICE:
            raise RuntimeError(
                "Port %d is occupied by %s; refusing to replace it."
                % (PORT, existing.get("service", "an unknown service"))
            )
    else:
        creationflags = 0
        if os.name == "nt":
            creationflags = 0x08000000 | 0x00000008 | 0x00000200
        subprocess.Popen(
            [sys.executable, str(SCRIPT_DIR / "tts_worker.py")],
            cwd=str(SCRIPT_DIR),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            creationflags=creationflags,
        )

    deadline = time.monotonic() + 180.0
    last = None
    while time.monotonic() < deadline:
        last = worker_status()
        if last and last.get("service") == SERVICE:
            if last.get("engine_ready"):
                emit(last)
                return
            if last.get("last_error"):
                raise RuntimeError(last["last_error"])
        time.sleep(0.5)
    raise RuntimeError("Narration worker did not become ready within 180 seconds: %r" % last)


def stop_existing(command):
    worker = worker_status()
    if not worker:
        emit({"ok": True, "running": False, "service": SERVICE})
        return
    worker_service = worker.get("service")
    if worker_service not in (SERVICE, LEGACY_SERVICE):
        raise RuntimeError(
            "Port %d is occupied by an unexpected service; refusing to control it." % PORT
        )
    remote_command = "clear" if command == "stop" else "shutdown"
    response = request({"command": remote_command}, timeout=5.0)
    response["detected_worker"] = worker_service
    emit(response)


def decode_text(value):
    if not value:
        raise RuntimeError("--text-base64 is required")
    try:
        text = base64.b64decode(value, validate=True).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as error:
        raise RuntimeError("--text-base64 must contain valid UTF-8 base64: %s" % error)
    text = text.strip()
    if not text:
        raise RuntimeError("Narration text must not be empty")
    if len(text) > 2000:
        raise RuntimeError("Narration text exceeds the 2000-character limit")
    return text


def speak(priority, text):
    worker = worker_status()
    if not worker or not worker.get("engine_ready"):
        raise RuntimeError("Narration is not ready; run 'tts.py start' first")
    emit(request({"command": "speak", "priority": priority, "text": text}, timeout=5.0))


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("install", "start", "status", "stop", "shutdown", "test"):
        commands.add_parser(name)
    speak_parser = commands.add_parser("speak")
    speak_parser.add_argument("--priority", choices=("routine", "pivotal"), default="routine")
    speak_parser.add_argument("--text-base64", default="")
    return parser


def main():
    args = build_parser().parse_args()
    if args.command == "status":
        emit(status())
    elif args.command == "install":
        install()
    elif args.command == "start":
        start()
    elif args.command in ("stop", "shutdown"):
        stop_existing(args.command)
    elif args.command == "test":
        speak("pivotal", "语音播报功能测试成功。曼波本地语音已经连接。")
    elif args.command == "speak":
        speak(args.priority, decode_text(args.text_base64))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as error:
        emit({"ok": False, "service": SERVICE, "voice": FIXED_VOICE, "error": str(error)})
        sys.exit(1)
