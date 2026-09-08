"""Cliente WebSocket del Bot, pensado para vivir dentro de Streamlit.

Mantiene UNA conexión abierta en un hilo de fondo. Por ahí salen los comandos y
por ahí entran tanto las respuestas (que se correlacionan por id) como los
eventos que el Bot empuja por su cuenta.

El hilo nunca toca la API de Streamlit: solo escribe en estructuras propias
protegidas por un lock, y la UI las lee en cada rerun.
"""

from __future__ import annotations

import queue
import socket
import subprocess
import sys
import threading
import time
from collections import deque
from pathlib import Path
from typing import Any

from websockets.sync.client import connect

import protocol
from config.settings import BOT_HOST, BOT_PORT

BASE_DIR = Path(__file__).resolve().parent.parent
RESPONSE_TIMEOUT = 30.0
MAX_EVENTS = 500


class BotClientError(Exception):
    """No se pudo completar el comando contra el Bot."""


class BotClient:
    def __init__(self, host: str = BOT_HOST, port: int = BOT_PORT):
        self.host = host
        self.port = port
        self.url = f"ws://{host}:{port}"

        self._outbox: queue.Queue[str] = queue.Queue()
        self._pending: dict[str, threading.Event] = {}
        self._responses: dict[str, protocol.Response] = {}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

        self.connected = False
        self.state: dict[str, Any] = {}
        self.events: deque[protocol.Event] = deque(maxlen=MAX_EVENTS)
        self.records: list[dict[str, Any]] = []
        self.event_seq = 0

    # --- ciclo de vida -----------------------------------------------------
    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="bot-client", daemon=True)
        self._thread.start()

    def close(self) -> None:
        self._stop.set()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                with connect(self.url, open_timeout=5) as conn:
                    self.connected = True
                    while not self._stop.is_set():
                        while True:
                            try:
                                conn.send(self._outbox.get_nowait())
                            except queue.Empty:
                                break
                        try:
                            raw = conn.recv(timeout=0.1)
                        except TimeoutError:
                            continue
                        self._handle(raw)
            except Exception:
                time.sleep(1.0)
            finally:
                self.connected = False

    def _handle(self, raw: str | bytes) -> None:
        try:
            data = protocol.decode(raw)
        except protocol.ProtocolError:
            return

        if data["type"] == protocol.TYPE_RESPONSE:
            response = protocol.Response.from_dict(data)
            with self._lock:
                if state := response.data.get("state"):
                    self.state = state
                self._responses[response.id] = response
                waiter = self._pending.get(response.id)
            if waiter:
                waiter.set()
            return

        if data["type"] == protocol.TYPE_EVENT:
            event = protocol.Event.from_dict(data)
            with self._lock:
                self.event_seq += 1
                self.events.append(event)
                if event.event == protocol.EVT_STATE:
                    self.state = event.payload
                elif event.event == protocol.EVT_RECORD:
                    self.records.append(event.payload)
                elif event.event == protocol.EVT_RUN_STARTED:
                    self.records.clear()

    # --- comandos ----------------------------------------------------------
    def send(
        self, cmd: str, payload: dict | None = None, timeout: float = RESPONSE_TIMEOUT
    ) -> protocol.Response:
        command = protocol.Command(cmd=cmd, payload=payload or {})
        waiter = threading.Event()
        with self._lock:
            self._pending[command.id] = waiter

        self._outbox.put(protocol.encode(command))
        if not waiter.wait(timeout):
            with self._lock:
                self._pending.pop(command.id, None)
            raise BotClientError(f"El Bot no respondió al comando '{cmd}' a tiempo")

        with self._lock:
            self._pending.pop(command.id, None)
            return self._responses.pop(command.id)

    # --- lectura para la UI ------------------------------------------------
    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return dict(self.state)

    def recent_events(self, limit: int = 40) -> list[protocol.Event]:
        with self._lock:
            return list(self.events)[-limit:]

    def all_records(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self.records)


def is_bot_running(host: str = BOT_HOST, port: int = BOT_PORT, timeout: float = 0.5) -> bool:
    """¿Hay algo escuchando en el puerto del Bot?"""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def ensure_bot_running(wait: float = 20.0) -> bool:
    """Arranca el proceso del Bot si no está corriendo, y espera a que responda.

    Así `streamlit run client/app.py` levanta todo solo, sin tener que abrir dos
    terminales.
    """
    if is_bot_running():
        return True

    creationflags = subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    subprocess.Popen(
        [sys.executable, "-m", "bot.server"],
        cwd=str(BASE_DIR),
        creationflags=creationflags,
    )

    deadline = time.time() + wait
    while time.time() < deadline:
        if is_bot_running():
            return True
        time.sleep(0.3)
    return False
