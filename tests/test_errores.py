"""Los errores que ve una persona deben poder leerse; el detalle técnico va al log."""

import time

from selenium.common.exceptions import TimeoutException, WebDriverException

import bot.session as sesion_mod
from core.process import BaseProcess
from core.utils.errores import mensaje_legible

# Así llega el volcado que Selenium añade a sus excepciones en Windows.
_VOLCADO = ["Symbols not available. Dumping unresolved backtrace:"] + [
    f"\t0x{0xff1213 + i:x}" for i in range(20)
]


def _selenium(mensaje: str) -> WebDriverException:
    return WebDriverException(mensaje, stacktrace=_VOLCADO)


def _es_legible(texto: str) -> bool:
    return "0x" not in texto and "Stacktrace" not in texto and "Session info" not in texto


def test_conexion_rechazada_se_explica_en_castellano():
    exc = _selenium("unknown error: net::ERR_CONNECTION_REFUSED\n  (Session info: chrome=143.0.7499.41)")
    texto = mensaje_legible(exc)
    assert texto.startswith("SIIF rechazó la conexión")
    assert _es_legible(texto)


def test_timeout_de_selenium_tiene_un_mensaje_claro():
    assert mensaje_legible(TimeoutException()) == "SIIF tardó demasiado en mostrar el elemento esperado."


def test_un_error_desconocido_conserva_solo_la_primera_linea_util():
    exc = _selenium("unknown error: algo raro\n  (Session info: chrome=143.0.7499.41)")
    assert mensaje_legible(exc) == "unknown error: algo raro"


def test_excepciones_normales_no_cambian():
    assert mensaje_legible(ValueError("dato inválido")) == "dato inválido"
    assert mensaje_legible(RuntimeError()) == "RuntimeError"


def test_un_fallo_de_selenium_dentro_del_proceso_deja_un_mensaje_corto():
    class _Proceso(BaseProcess):
        def execute(self, **_data):
            try:
                raise TimeoutException()
            except Exception as exc:
                return self._handle_exception(exc)

    ok, mensaje = _Proceso(object()).execute()
    assert ok is False
    assert mensaje == "Error en proceso _Proceso: SIIF tardó demasiado en mostrar el elemento esperado."


def test_login_con_siif_caido_muestra_un_mensaje_legible(monkeypatch):
    class _Driver:
        def get(self, url):
            raise _selenium(
                "unknown error: net::ERR_CONNECTION_REFUSED\n  (Session info: chrome=143.0.7499.41)"
            )

    class _Chrome:
        def create_driver(self):
            return _Driver()

        def quit_driver(self):
            return None

    monkeypatch.setattr(sesion_mod, "ChromeDriver", _Chrome)
    sesion = sesion_mod.BotSession(emit=lambda _e, _p: None)

    sesion.login("usuario", "clave")
    for _ in range(100):
        if not sesion.connecting:
            break
        time.sleep(0.05)

    assert sesion.last_message.startswith("No se pudo abrir la sesión: SIIF rechazó la conexión")
    assert _es_legible(sesion.last_message)
    assert sesion.logged_in is False
