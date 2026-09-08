from datetime import datetime
from pathlib import Path

import polars as pl

from config.settings import ERROR_FILE_PATH, INPUT_FILE_PATH, OUTPUT_FILE_PATH


class DataManager:
    """
    Encapsula la carga y guardado de archivos de Excel usando Polars.
    Tiene dos métodos principales:

    - load_input: carga Excel con tipo de dato string.
    - update_entries: elimina registros ya procesados del archivo de entrada.
    """

    def __init__(self, input_path: Path = INPUT_FILE_PATH):
        self.input_path = input_path
        self._records_success: list[dict] = []
        self._records_failure: list[dict] = []

    def load_input(self) -> pl.DataFrame:
        """
        Carga el archivo de Excel de entrada y devuelve un DataFrame de Polars.
        Todos los datos se cargan como strings para evitar problemas de tipo.
        """
        try:
            df = pl.read_excel(self.input_path, infer_schema_length=0)
            return df
        except Exception as e:
            print(f"Error al cargar el archivo de entrada: {e}")
            raise

    def update_entries(self, processed_ids: list):
        """
        Elimina los registros que ya han sido procesados del archivo de entrada.
        Se asume que hay una columna 'INDEX' que identifica de manera única cada registro.

        :param processed_ids: Lista de IDs que han sido procesados y deben ser eliminados.
        """
        try:
            df = self.load_input()
            updated_df = df.filter(~pl.col("INDEX").is_in(processed_ids))
            updated_df.write_excel(self.input_path)
        except Exception as e:
            print(f"Error al actualizar el archivo de entrada: {e}")
            raise

    def observe_process(self, is_success: bool, record: dict, message: str):
        print(record)
        row = {
            "INDEX": record.get("INDEX", ""),
            "FECHA": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "NUMERO_CUENTA": record.get(
                "NUMERO_CUENTA", ""
            ),  # Definir los campos que se desean guardar
            "NOMBRE_CUENTA": record.get("NOMBRE_CUENTA", ""),
            "MESSAGE": message,
        }

        if is_success:
            self._records_success.append(row)
        else:
            self._records_failure.append(row)

        print(f"Registro procesado: {row}")

    def save_observers(self):
        if self._records_success:
            df_success = pl.DataFrame(self._records_success)
            df_success.write_excel(OUTPUT_FILE_PATH)

        if self._records_failure:
            df_failure = pl.DataFrame(self._records_failure)
            df_failure.write_excel(ERROR_FILE_PATH)

        print(
            f"Resultados guardados. Éxitos: {len(self._records_success)}, Fallidos: {len(self._records_failure)}"
        )
