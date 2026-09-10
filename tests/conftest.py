import pytest

import config.settings as settings


@pytest.fixture()
def rutas(tmp_path, monkeypatch):
    """Redirige salidas, errores y trazabilidad a una carpeta temporal."""
    monkeypatch.setattr(settings, "TRACE_DIR", tmp_path / "trazabilidad")
    monkeypatch.setattr(settings, "OUTPUT_FILE_PATH", tmp_path / "salidas" / "CONCILIACION.xlsx")
    monkeypatch.setattr(settings, "ERROR_FILE_PATH", tmp_path / "errores" / "ERRORES.xlsx")
    return tmp_path, tmp_path / "ENTRADAS.xlsx"
