import logging
from pathlib import Path

import polars as pl

from config.settings import INPUT_FILE_PATH

logger = logging.getLogger(__name__)


class DataManager:
    """Lectura del Excel de entrada y retirada de los registros ya procesados.

    Los resultados ya no pasan por aquí: los registran los observadores de la
    corrida (services/observers).
    """

    def __init__(self, input_path: Path = INPUT_FILE_PATH):
        self.input_path = input_path

    def load_input(self) -> pl.DataFrame:
        """Todo como texto, para no depender de cómo tipó Excel cada columna."""
        try:
            return pl.read_excel(self.input_path, infer_schema_length=0)
        except Exception:
            logger.exception("No se pudo cargar el archivo de entrada %s", self.input_path)
            raise

    def update_entries(self, processed_ids: list) -> None:
        """Elimina del Excel de entrada las filas cuyo INDEX ya fue procesado."""
        df = self.load_input()
        df.filter(~pl.col("INDEX").is_in(processed_ids)).write_excel(self.input_path)
