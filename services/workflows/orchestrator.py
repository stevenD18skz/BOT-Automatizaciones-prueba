from config.settings import BATCH_SIZE, SIIF_URL
from core import ChromeDriver
from core.base import BasePage
from services.data.data_manager import DataManager
from services.processes.login_siif import SIIFLoginProcess
from services.processes.search_account_name import SearchAccountName
from ui.login import get_credentials


class Orchestrator:
    def __init__(self):
        is_sucess, username, password = get_credentials()
        if not is_sucess:
            raise ValueError("No se pudieron obtener las credenciales")
        self.username = username
        self.password = password

        self.data_manager = DataManager()

    def run(self):
        with ChromeDriver() as driver:
            page = BasePage(driver)
            login_process = SIIFLoginProcess(page)
            searcher_process = SearchAccountName(driver)

            # 0. Preparar el entorno: abrir el navegador y navegar a la URL de SIIF
            page.navigate_to(SIIF_URL)

            # 1. Login (una vez)
            is_login, msg_login = login_process.execute(self.username, self.password)
            if not is_login:
                return

            # 2. Lectura del insumo
            df = self.data_manager.load_input()

            # 3. Iteración sobre cada registro en tipo diccionario del DataFrame
            idx = 0
            processed_ids = []

            for row in df.to_dicts():
                idx += 1
                if idx % BATCH_SIZE == 0:
                    self.data_manager.update_entries(processed_ids)
                    processed_ids = []

                # Procesar cada registro
                is_success, msg = searcher_process.execute(**row)

                # Añadir variables del proceso al registro original para guardar resultados
                row["NOMBRE_CUENTA"] = searcher_process.get_variable("NOMBRE_CUENTA")

                # Observar el resultado del proceso para cada registro
                self.data_manager.observe_process(is_success, row, msg)
                processed_ids.append(row["INDEX"])

            # 4. Guardar resultados exitosos y fallidos
            self.data_manager.save_observers()

            # 5. Limpiar el archivo de entrada eliminando los registros procesados
            self.data_manager.update_entries(processed_ids)
            print("Proceso finalizado exitosamente.")
