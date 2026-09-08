"""Servidor WebSocket del Bot.

Corre en su propio proceso (`python -m bot.server`). La UI de Streamlit se
conecta y le manda comandos; el Bot responde a cada comando y, además, empuja
eventos de avance mientras trabaja, sin que la UI tenga que preguntar.

Selenium es bloqueante, así que el trabajo pesado sale del event loop:
    - login/logout      -> asyncio.to_thread (responde cuando termina)
    - execute           -> hilo propio en BotSession (responde "iniciado" ya)
    - ping/status/stop  -> se atienden siempre, aunque haya un lote corriendo
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from websockets.asyncio.server import ServerConnection, serve  # noqa: E402
from websockets.exceptions import ConnectionClosed  # noqa: E402

import protocol  # noqa: E402
from bot.session import BotBusyError, BotSession  # noqa: E402
from config.settings import BOT_HOST, BOT_PORT, BOT_NAME  # noqa: E402
from core.utils.logging import setup_logging  # noqa: E402

ICONS = {
    protocol.EVT_LOG: "·",
    protocol.EVT_STATE: "≡",
    protocol.EVT_RUN_STARTED: "▶",
    protocol.EVT_PROGRESS: "→",
    protocol.EVT_RECORD: "✓",
    protocol.EVT_RUN_FINISHED: "■",
}


class BotServer:
    def __init__(self, host: str = BOT_HOST, port: int = BOT_PORT):
        self.host = host
        self.port = port
        self._clients: set[ServerConnection] = set()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._session = BotSession(emit=self._emit)

    # --- envío de eventos --------------------------------------------------
    def _emit(self, event: str, payload: dict) -> None:
        """Programa el envío de un evento. Seguro desde cualquier hilo."""
        self._print_event(event, payload)
        if self._loop is None:
            return
        asyncio.run_coroutine_threadsafe(
            self._broadcast(protocol.Event(event, payload)), self._loop
        )

    def _print_event(self, event: str, payload: dict) -> None:
        icon = ICONS.get(event, "•")
        if event == protocol.EVT_PROGRESS:
            detail = f"{payload.get('current')}/{payload.get('total')} {payload.get('numero_cuenta', '')}"
        elif event == protocol.EVT_RECORD:
            icon = "✓" if payload.get("ok") else "✗"
            detail = f"{payload.get('numero_cuenta', '')} → {payload.get('message', '')}"
        elif event == protocol.EVT_LOG:
            detail = payload.get("message", "")
        elif event == protocol.EVT_STATE:
            return  # demasiado ruidoso para consola
        else:
            detail = str(payload)
        print(f"  {icon} [{event}] {detail}", flush=True)

    async def _broadcast(self, event: protocol.Event) -> None:
        if not self._clients:
            return
        raw = protocol.encode(event)
        await asyncio.gather(
            *(self._safe_send(client, raw) for client in tuple(self._clients)),
            return_exceptions=True,
        )

    async def _safe_send(self, client: ServerConnection, raw: str) -> None:
        try:
            await client.send(raw)
        except ConnectionClosed:
            self._clients.discard(client)

    # --- ciclo de vida -----------------------------------------------------
    async def start(self) -> None:
        self._loop = asyncio.get_running_loop()
        async with serve(self._handle_client, self.host, self.port):
            print(f"\n{'=' * 60}")
            print(f"  {BOT_NAME} — servidor WebSocket")
            print(f"  Escuchando en ws://{self.host}:{self.port}")
            print(f"  Ctrl+C para detener")
            print(f"{'=' * 60}\n", flush=True)
            logging.info(f"Servidor WebSocket escuchando en ws://{self.host}:{self.port}")
            await asyncio.Future()

    async def _handle_client(self, websocket: ServerConnection) -> None:
        self._clients.add(websocket)
        print(f"  ⇄ cliente conectado ({len(self._clients)} activos)", flush=True)
        try:
            await websocket.send(
                protocol.encode(
                    protocol.Event(protocol.EVT_STATE, self._session.snapshot())
                )
            )
            async for raw in websocket:
                await self._on_message(websocket, raw)
        except ConnectionClosed:
            pass
        finally:
            self._clients.discard(websocket)
            print(f"  ⇄ cliente desconectado ({len(self._clients)} activos)", flush=True)

    async def _on_message(self, websocket: ServerConnection, raw: str | bytes) -> None:
        try:
            command = protocol.Command.from_dict(protocol.decode(raw))
        except protocol.ProtocolError as exc:
            await websocket.send(
                protocol.encode(protocol.Response(id="", ok=False, message=str(exc)))
            )
            return

        print(f"  ⌁ comando: {command.cmd}", flush=True)
        response = await self._dispatch(command)
        response.data["state"] = self._session.snapshot()
        await websocket.send(protocol.encode(response))

    async def _dispatch(self, command: protocol.Command) -> protocol.Response:
        def reply(ok: bool, message: str = "", **data) -> protocol.Response:
            return protocol.Response(id=command.id, ok=ok, message=message, data=data)

        try:
            if command.cmd == protocol.CMD_PING:
                return reply(True, "pong")

            if command.cmd == protocol.CMD_STATUS:
                return reply(True, "Estado actual")

            if command.cmd == protocol.CMD_STOP:
                ok, message = self._session.request_stop()
                return reply(ok, message)

            if command.cmd == protocol.CMD_LOGIN:
                username = str(command.payload.get("username", "")).strip()
                password = str(command.payload.get("password", ""))
                if not username or not password:
                    return reply(False, "Usuario y contraseña son obligatorios")
                ok, message = self._session.login(username, password)
                return reply(ok, message)

            if command.cmd == protocol.CMD_EXECUTE:
                ok, message = self._session.execute()
                return reply(ok, message)

            if command.cmd == protocol.CMD_DEMO:
                ok, message = self._session.demo(
                    registros=int(command.payload.get("registros", 12)),
                    pausa=float(command.payload.get("pausa", 1.0)),
                )
                return reply(ok, message)

            if command.cmd == protocol.CMD_LOGOUT:
                ok, message = await asyncio.to_thread(self._session.logout)
                return reply(ok, message)

            return reply(False, f"Comando no implementado: {command.cmd}")

        except BotBusyError as exc:
            return reply(False, str(exc))
        except Exception as exc:
            logging.exception(f"Error atendiendo el comando {command.cmd}")
            return reply(False, f"Error interno: {exc}")


def _disable_quick_edit() -> None:
    """Desactiva el modo selección de la consola de Windows.

    Con QuickEdit activo, un clic dentro de la ventana pausa toda escritura a
    stdout: el `print` del event loop se bloquea y el servidor deja de aceptar
    conexiones sin dar ningún error.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-10)  # STD_INPUT_HANDLE
        mode = wintypes.DWORD()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return
        enable_quick_edit = 0x0040
        enable_extended_flags = 0x0080
        kernel32.SetConsoleMode(
            handle, (mode.value & ~enable_quick_edit) | enable_extended_flags
        )
    except Exception:
        pass


def main() -> None:
    # La consola de Windows suele venir en cp1252 y reventaría con los iconos.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    _disable_quick_edit()

    setup_logging()
    server = BotServer()
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\n  Servidor detenido por el usuario", flush=True)


if __name__ == "__main__":
    main()
