"""Jedan motor po stroju. Sučelje koje dođe drugo samo gleda dnevnik."""

from __future__ import annotations

import os
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from doxa.config import LOCK_PATH
from doxa.engine import Engine
from doxa.market import MarketHub


@dataclass
class Handle:
    role: str
    engine: Engine | None
    hub: MarketHub


def _named(name: str):
    for thread in threading.enumerate():
        if thread.name == name:
            return thread
    return None


def get_hub() -> MarketHub:
    existing = _named("doxa-market")
    hub = getattr(existing, "hub", None) if existing else None
    if hub is not None:
        return hub
    hub = MarketHub()
    thread = threading.Thread(target=hub.run, name="doxa-market", daemon=True)
    thread.hub = hub
    thread.start()
    return hub


def _lock_path() -> Path:
    override = os.getenv("DOXA_LOCK", "").strip()
    return Path(override or LOCK_PATH)


def _acquire_lock():
    """Jedan motor po računalu. Na Windowsu nema fcntl, pa se zaključava preko msvcrt."""
    path = _lock_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(path, "a+b")
    try:
        if handle.seek(0, os.SEEK_END) == 0:
            handle.write(b"\0")
            handle.flush()
        handle.seek(0)
        if sys.platform == "win32":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        return None
    return handle


def _trade_loop(engine: Engine, hub: MarketHub) -> None:
    last_error = ""
    while True:
        try:
            engine.tick(hub.snapshot())
            last_error = ""
        except Exception as exc:
            message = str(exc)[:180]
            if message and message != last_error:
                last_error = message
                with engine._lock:
                    engine._note("Tick greška: " + message)
        time.sleep(1.0)


def ensure_started() -> Handle:
    hub = get_hub()
    existing = _named("doxa-engine")
    engine = getattr(existing, "engine", None) if existing else None
    if engine is not None:
        return Handle("engine", engine, hub)
    lock = _acquire_lock()
    if lock is None:
        return Handle("viewer", None, hub)
    engine = Engine.load()
    thread = threading.Thread(target=_trade_loop, args=(engine, hub), name="doxa-engine", daemon=True)
    thread.engine = engine
    thread.lock_file = lock
    thread.start()
    return Handle("engine", engine, hub)
