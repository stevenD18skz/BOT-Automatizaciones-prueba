"""Contrato compartido entre el cliente (Streamlit) y el servidor (Bot).

Los dos procesos importan este mismo módulo. Si cambias el nombre de un comando
o la forma de un evento, cámbialo aquí una sola vez y ambos lados quedan
sincronizados.

Hay tres tipos de mensaje que viajan por el WebSocket:

    command   cliente -> servidor   "haz esto"            (lleva un id)
    response  servidor -> cliente   "resultado de tu id"  (mismo id)
    event     servidor -> cliente   "esto está pasando"   (sin id, no lo pediste)

Los eventos son la razón de usar WebSocket en vez de un socket TCP de
petición/respuesta: el Bot puede empujar avances a la UI mientras trabaja, sin
que la UI tenga que estar preguntando.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

PROTOCOL_VERSION = 1

# --- Tipos de sobre ---------------------------------------------------------
TYPE_COMMAND = "command"
TYPE_RESPONSE = "response"
TYPE_EVENT = "event"

# --- Comandos: cliente -> servidor -----------------------------------------
CMD_PING = "ping"
CMD_STATUS = "status"
CMD_LOGIN = "login"
CMD_LOGOUT = "logout"
CMD_EXECUTE = "execute"
CMD_STOP = "stop"

KNOWN_COMMANDS = frozenset(
    {CMD_PING, CMD_STATUS, CMD_LOGIN, CMD_LOGOUT, CMD_EXECUTE, CMD_STOP}
)

# --- Eventos: servidor -> cliente ------------------------------------------
EVT_LOG = "log"
EVT_STATE = "state"
EVT_RUN_STARTED = "run_started"
EVT_PROGRESS = "progress"
EVT_RECORD = "record"
EVT_RUN_FINISHED = "run_finished"


class ProtocolError(Exception):
    """El mensaje recibido no cumple el contrato."""


@dataclass
class Command:
    """Petición del cliente al Bot."""

    cmd: str
    payload: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": TYPE_COMMAND,
            "version": PROTOCOL_VERSION,
            "id": self.id,
            "cmd": self.cmd,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Command:
        cmd = data.get("cmd")
        if cmd not in KNOWN_COMMANDS:
            raise ProtocolError(f"Comando desconocido: {cmd!r}")
        payload = data.get("payload") or {}
        if not isinstance(payload, dict):
            raise ProtocolError("El payload debe ser un objeto")
        return cls(cmd=cmd, payload=payload, id=str(data.get("id") or uuid.uuid4()))


@dataclass
class Response:
    """Respuesta del Bot a un comando concreto, correlacionada por `id`."""

    id: str
    ok: bool
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": TYPE_RESPONSE,
            "version": PROTOCOL_VERSION,
            "id": self.id,
            "ok": self.ok,
            "message": self.message,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Response:
        return cls(
            id=str(data.get("id", "")),
            ok=bool(data.get("ok", False)),
            message=str(data.get("message", "")),
            data=data.get("data") or {},
        )


@dataclass
class Event:
    """Aviso que el Bot empuja por su cuenta mientras trabaja."""

    event: str
    payload: dict[str, Any] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": TYPE_EVENT,
            "version": PROTOCOL_VERSION,
            "event": self.event,
            "payload": self.payload,
            "ts": self.ts,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Event:
        return cls(
            event=str(data.get("event", "")),
            payload=data.get("payload") or {},
            ts=float(data.get("ts", time.time())),
        )


def encode(message: Command | Response | Event) -> str:
    """Serializa un mensaje a JSON listo para mandar por el socket."""
    return json.dumps(message.to_dict(), ensure_ascii=False)


def decode(raw: str | bytes) -> dict[str, Any]:
    """Convierte el JSON crudo del socket en un diccionario validado."""
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProtocolError(f"JSON inválido: {exc}") from exc
    if not isinstance(data, dict):
        raise ProtocolError("El mensaje debe ser un objeto JSON")
    if data.get("type") not in {TYPE_COMMAND, TYPE_RESPONSE, TYPE_EVENT}:
        raise ProtocolError(f"Tipo de mensaje desconocido: {data.get('type')!r}")
    return data
