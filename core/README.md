# Framework RPA Core

## Descripción

Este es el núcleo del framework RPA que proporciona una base sólida y extensible para la construcción de bots de automatización web. Ha sido diseñado con principios de arquitectura limpia y siguiendo las mejores prácticas para sistemas de transacciones.

## Arquitectura

### Componentes Principales

#### 1. `ProcessInterface` (interfaces.py)

Interfaz base que define el contrato que deben cumplir todos los procesos RPA:

- **Método obligatorio**: `execute(**kwargs) -> tuple[bool, str]`
- **Gestión de variables**: Métodos para guardar y extraer variables del proceso
- **Consistencia**: Garantiza que todos los procesos retornen el mismo formato

#### 2. `BasePage` (base.py)

Clase base para interacciones con páginas web que incluye:

- **Esperas robustas**: Todos los métodos usan explicit waits
- **Manejo de errores**: Logging detallado y manejo de excepciones
- **Métodos útiles**: Click seguro, input de texto, selección de dropdowns, etc.
- **Transacciones**: Diseñado para sistemas transaccionales donde cada elemento debe estar cargado

#### 3. `BaseProcess` (process.py)

Implementación base para procesos RPA que combina:

- **ProcessInterface**: Implementa la interfaz requerida
- **BasePage**: Acceso a funcionalidades web a través de `self.page`
- **Logging**: Sistema de logging integrado
- **Variables**: Gestión automática de variables del proceso

#### 4. `ChromeDriver` (driver_manager.py)

Gestor del ciclo de vida de Chrome WebDriver que incluye:

- **Gestión automática**: Instalación y configuración automática de ChromeDriver
- **Opciones optimizadas**: Configuración de Chrome para rendimiento RPA
- **Context manager**: Soporte para `with` statements para limpieza automática
- **Manejo de errores**: Logging detallado y limpieza de recursos
- **Cache de drivers**: Reutilización eficiente de binarios descargados

#### 5. Utilidades (utils/)

- **waiters.py**: Funciones de espera robustas para elementos
- **context.py**: Context managers para frames
- **logging.py**: Configuración de logging

## Uso del Framework

### 1. Implementar un Proceso

```python
from selenium.webdriver.common.by import By
from core import BaseProcess

class MiProceso(BaseProcess):
    def execute(self, parametro1: str, parametro2: int) -> tuple[bool, str]:
        try:
            self._log_execution_start(parametro1=parametro1, parametro2=parametro2)

            # Usar métodos de BasePage a través de self.page
            self.page.navigate_to("https://ejemplo.com")
            self.page.wait_and_input_text((By.ID, "input"), parametro1)
            self.page.wait_and_click((By.ID, "submit"))

            # Guardar variables del proceso
            self.set_variable("resultado", "valor_extraido")
            self.set_variable("timestamp", "2024-01-01")

            message = "Proceso ejecutado exitosamente"
            self._log_execution_end(True, message)
            return True, message

        except Exception as e:
            return self._handle_exception(e)
```

### 2. Ejecutar el Proceso

#### Opción A: Usando ChromeDriver (Recomendado)

```python
from core import BaseProcess, ChromeDriver

# Usar ChromeDriver como gestor de contexto
with ChromeDriver() as driver:
    # Crear instancia del proceso
    mi_proceso = MiProceso(driver)

    # Ejecutar el proceso
    exito, mensaje = mi_proceso.execute(
        parametro1="valor1",
        parametro2=123
    )

    if exito:
        print(f"{mensaje}")
        # Extraer variables generadas
        variables = mi_proceso.get_variables()
        print(f"Resultado: {variables.get('resultado')}")
    else:
        print(f"{mensaje}")

    # El driver se cierra automáticamente
```

#### Opción B: Gestión manual de driver

```python
from core import BaseProcess, ChromeDriver

# Crear driver manualmente
chrome_driver = ChromeDriver()
driver = chrome_driver.create_driver()

try:
    # Crear instancia del proceso
    mi_proceso = MiProceso(driver)

    # Ejecutar el proceso
    exito, mensaje = mi_proceso.execute(
        parametro1="valor1",
        parametro2=123
    )

    if exito:
        print(f"{mensaje}")
        variables = mi_proceso.get_variables()
        print(f"Resultado: {variables.get('resultado')}")
    else:
        print(f"{mensaje}")

finally:
    chrome_driver.quit_driver()
```

## Principios del Framework

### 1. **Wait-Based Architecture**

- Todos los métodos de interacción usan explicit waits
- Garantiza que los elementos estén cargados antes de interactuar
- Esencial para sistemas transaccionales

### 2. **Consistent Interface**

- Todos los procesos implementan `ProcessInterface`
- Método `execute()` siempre retorna `tuple[bool, str]`
- Permite composición y orquestación de procesos

### 3. **Variable Management**

- Los procesos pueden generar y extraer variables
- Útil para pasar datos entre subprocesos
- Facilita la depuración y monitoreo

### 4. **Robust Error Handling**

- Logging detallado en todos los niveles
- Manejo consistente de excepciones
- Información contextual para debugging

### 5. **Separation of Concerns**

- `BasePage`: Interacciones web
- `BaseProcess`: Lógica de negocio
- `ProcessInterface`: Contrato común

## Métodos Disponibles en BasePage

### Interacciones Básicas

- `find_element()`, `find_elements()`
- `click()`, `wait_and_click()`
- `input_text()`, `wait_and_input_text()`
- `get_text()`, `wait_get_text()`

### Esperas y Verificaciones

- `wait_for_element()`, `wait_for_element_visible()`
- `wait_for_element_invisible()`, `is_element_present()`
- `is_element_clickable()`, `wait_for_page_load()`

### Interacciones Avanzadas

- `select_dropdown_by_text()`, `select_dropdown_by_value()`
- `get_attribute()`, `scroll_to_element()`
- `execute_script()`, `refresh_page()`

### Navegación y Frames

- `navigate_to()`, `get_current_url()`
- `change_frame()`, `change_frame_default()`
- `accept_alert()`

## Mejores Prácticas

### 1. Estructura de Procesos

```python
def execute(self, **kwargs) -> tuple[bool, str]:
    try:
        # 1. Log inicio
        self._log_execution_start(**kwargs)

        # 2. Validaciones previas
        if not self._validate_inputs(**kwargs):
            return False, "Parámetros inválidos"

        # 3. Lógica principal
        # ... código del proceso ...

        # 4. Guardar variables
        self.set_variable("key", "value")

        # 5. Log éxito y retornar
        self._log_execution_end(True, message)
        return True, message

    except Exception as e:
        return self._handle_exception(e)
```

### 2. Localizadores

Definir localizadores como constantes al inicio:

```python
USERNAME_INPUT = (By.ID, "username")
PASSWORD_INPUT = (By.NAME, "password")
LOGIN_BUTTON = (By.XPATH, "//button[@type='submit']")
```

### 3. Uso de Variables

```python
# Guardar datos importantes
self.set_variable("numero_transaccion", numero)
self.set_variable("monto_procesado", monto)

# En otro proceso, extraer variables
numero = proceso_anterior.get_variable("numero_transaccion")
```

## ChromeDriver - Gestión de WebDriver

### Características

El `ChromeDriver` proporciona gestión robusta del ciclo de vida de Chrome WebDriver:

- **Instalación automática**: Usa `webdriver-manager` para descargar y mantener ChromeDriver
- **Configuración optimizada**: Aplica automáticamente las opciones definidas en `settings.py`
- **Gestión de caché**: Reutiliza drivers descargados para mejorar el rendimiento
- **Context manager**: Implementa `__enter__` y `__exit__` para limpieza automática
- **Timeouts configurados**: Aplica automáticamente timeouts de página y búsqueda
- **Logging integrado**: Registra todas las operaciones importantes

### Uso Básico

#### Como Context Manager (Recomendado)

```python
from core import ChromeDriver, BasePage

with ChromeDriver() as driver:
    page = BasePage(driver)
    page.navigate_to("https://example.com")
    # El driver se cierra automáticamente
```

#### Gestión Manual

```python
from core import ChromeDriver

chrome_driver = ChromeDriver()
driver = chrome_driver.create_driver()

# Usar el driver...

chrome_driver.quit_driver()  # Limpieza manual
```

#### Integración con BaseProcess

```python
from core import BaseProcess, ChromeDriver

class MiProceso(BaseProcess):
    def __init__(self):
        super().__init__()
        self.chrome_driver = None

    def setup(self):
        self.chrome_driver = ChromeDriver()
        driver = self.chrome_driver.create_driver()
        self.page = BasePage(driver)

    def cleanup(self):
        if self.chrome_driver:
            self.chrome_driver.quit_driver()
```

### Configuración

El `ChromeDriver` usa las configuraciones definidas en `config/settings.py`:

```python
# Chrome Options aplicadas automáticamente
CHROME_OPTIONS = {
    "headless": False,           # Modo visible
    "start-maximized": True,     # Ventana maximizada
    "disable-extensions": True,  # Sin extensiones
    "disable-infobars": True,    # Sin barras de información
}

# Timeouts aplicados automáticamente
TIMEOUT_PAGE_LOAD = 45   # Timeout para carga de página
TIMEOUT_SEARCH = 20      # Timeout para búsqueda de elementos

# Directorio de caché para drivers
DRIVER_CACHE_DIR = BASE_DIR / "src" / "drivers"
```

### Métodos Disponibles

- `create_driver()` - Crea una nueva instancia de Chrome WebDriver
- `quit_driver()` - Cierra el driver y libera recursos
- `_setup_driver_cache()` - Configura el directorio de caché
- `_configure_chrome_options()` - Aplica opciones de Chrome
- `_get_driver_path()` - Obtiene la ruta del ChromeDriver

## Extensibilidad

El framework está diseñado para ser extensible:

1. **Nuevos métodos en BasePage**: Agregar funcionalidades web específicas
2. **Procesos especializados**: Heredar de BaseProcess para dominios específicos
3. **Utilidades personalizadas**: Agregar helpers en utils/
4. **Interfaces adicionales**: Definir contratos para casos específicos
5. **Drivers adicionales**: Extender ChromeDriver para otros navegadores

## Ejemplos Completos

Ver `examples.py` para ejemplos detallados de:

- Proceso de login
- Extracción de datos
- Llenado de formularios
- Uso de variables entre procesos
