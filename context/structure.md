# Estructura del Proyecto RPA

## Organización General

### Estructura de Directorios

```text
proyecto-rpa/
├── src/                           # Código fuente principal
│   ├── config/                    # Configuración centralizada
│   │   ├── settings.py           # Parámetros del sistema
│   │   └── __pycache__/          # Cache compilado Python
│   ├── core/                      # Módulo RPA core
│   │   ├── __init__.py           # Inicialización del módulo
│   │   ├── base.py               # Clase base para procesos
│   │   ├── constants.py          # Constantes del sistema
│   │   ├── driver_manager.py     # Gestión de navegadores
│   │   ├── interfaces.py         # Interfaces y contratos
│   │   ├── process.py            # Lógica de procesamiento
│   │   ├── utils/                # Utilidades del core
│   │   │   ├── __init__.py      # Inicialización utilidades
│   │   │   ├── context.py       # Gestión de contexto
│   │   │   ├── helpers.py       # Funciones auxiliares
│   │   │   ├── logging.py       # Configuración de logs
│   │   │   └── waiters.py       # Esperas inteligentes
│   │   └── README.md            # Documentación del core
│   ├── services/                 # Servicios especializados
│   │   ├── data/                # Gestión de datos
│   │   │   └── data_manager.py  # Controlador de archivos Excel
│   │   ├── navigation/          # Servicios de navegación
│   │   │   └── navigator.py     # Coordinador de navegación web
│   │   ├── observers/           # Patrón Observer
│   │   │   ├── error.py         # Observador de errores
│   │   │   └── success.py       # Observador de éxitos
│   │   ├── processes/           # Procesos específicos
│   │   │   ├── login.py         # Proceso de autenticación
│   │   │   └── [proceso].py     # Procesos del negocio
│   │   └── workflows/           # Orquestación
│   │       └── orchestrator.py  # Coordinador principal
│   ├── ui/                      # Interfaces de usuario
│   │   └── login.py            # Diálogo de credenciales
│   ├── data/                    # Datos de configuración
│   ├── logs/                    # Archivos de registro
│   │   └── rpa.log             # Log principal del sistema
│   └── main.py                  # Punto de entrada principal
├── entradas/                    # Archivos de entrada
│   └── ENTRADAS.xlsx           # Datos para procesamiento
├── salidas/                     # Archivos de salida exitosa
│   └── CONCILIACION.xlsx       # Resultados consolidados
├── errores/                     # Archivos de errores
│   └── ERRORES.xlsx            # Registro de fallos
├── documentación/               # Documentación del proyecto
├── pyproject.toml              # Configuración Poetry
├── poetry.lock                 # Bloqueo de dependencias
├── INSTALAR-CONFIGURAR.bat     # Script de instalación
├── EJECUTABLE.bat              # Script de ejecución
└── README.md                   # Documentación principal
```

## Configuración Inicial

### Archivo settings.py

El archivo de configuración centralizada debe contener los siguientes elementos:

```python
from pathlib import Path

# URL del sistema objetivo
SISTEMA_URL = "http://sistema.ejemplo.com/"

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Configuración de archivos Excel
INPUT_FILE_PATH = BASE_DIR / "entradas" / "ENTRADAS.xlsx"
OUTPUT_FILE_PATH = BASE_DIR / "salidas" / "CONCILIACION.xlsx"
ERROR_FILE_PATH = BASE_DIR / "errores" / "ERRORES.xlsx"

# Configuración de procesamiento
BATCH_SIZE = 100

# Configuración de navegación
MENU_ROUTE = {
    "menu": "Menu Principal",
    "submenu": "Submenu Especifico",
    "processes": {
        "proceso_principal": {
            "name": "nombre_proceso",
            "id": "Identificador del Proceso",
        },
    },
}
```

## Stack Tecnológico

### Lenguaje Base

#### Python 3.13.x

- Versión mínima requerida para compatibilidad con todas las dependencias
- Soporte completo para typing hints y características modernas
- Optimizaciones de rendimiento necesarias para automatización

### Gestión de Dependencias

#### Poetry

- Gestión de entornos virtuales integrada
- Control de versiones de dependencias reproducible
- Separación clara entre dependencias de desarrollo y producción

```toml
[tool.poetry]
name = "proyecto-rpa"
version = "1.0.0"
description = "Sistema de automatización RPA"
authors = ["Equipo Desarrollo <equipo@empresa.com>"]

[tool.poetry.dependencies]
python = "^3.13"
selenium = "^4.15.0"
webdriver-manager = "^4.0.0"
polars = "^0.20.0"
pandas = "^2.1.0"
beautifulsoup4 = "^4.12.0"
fastexcel = "^0.9.0"
openpyxl = "^3.1.0"

[tool.poetry.group.dev.dependencies]
ruff = "^0.1.0"
```

### Automatización Web

#### Selenium WebDriver

- Control programático de navegadores web
- Interacción con elementos dinámicos
- Gestión de JavaScript y AJAX

#### WebDriver Manager

- Descarga automática de drivers de navegador
- Gestión de versiones de ChromeDriver
- Compatibilidad automática con versiones de Chrome

### Procesamiento de Datos

#### Polars

- Procesamiento eficiente de DataFrames
- Mejor rendimiento que pandas para archivos grandes
- API moderna y expresiva

**Pandas** (uso ocasional)

- Lectura de datos complejos desde HTML
- Compatibilidad con sistemas legacy
- Funciones específicas no disponibles en Polars

### Web Scraping

#### BeautifulSoup4

- Análisis de HTML complejo
- Extracción de datos de páginas web
- Navegación de DOM estructurado

### Manejo de Excel

#### FastExcel

- Lectura rápida de archivos Excel grandes
- Optimización de memoria para datasets extensos

#### OpenPyXL

- Escritura de archivos Excel con formato
- Manipulación de hojas y celdas específicas
- Soporte completo para fórmulas y estilos

### Calidad de Código

#### Ruff

- Linting rápido y completo
- Formateo automático de código
- Configuración unificada para múltiples herramientas

## Estructura de Automatización

### Directorio src/

Contiene todo el código fuente organizado por responsabilidades:

#### config/

- `settings.py`: Configuración centralizada del sistema
- Parámetros modificables sin cambiar código
- URLs, rutas de archivos, timeouts, configuraciones de navegador

#### core/

Módulo central de automatización RPA:

- `base.py`: Clase abstracta BaseProcess para todos los procesos
- `constants.py`: Constantes inmutables del sistema
- `driver_manager.py`: Gestión del ciclo de vida del navegador
- `interfaces.py`: Contratos y protocolos del sistema
- `process.py`: Lógica común de procesamiento
- `utils/`: Utilidades transversales del core

#### services/

Servicios especializados por dominio:

- `data/`: Gestión de entrada y salida de datos Excel
- `navigation/`: Coordinación de navegación web
- `observers/`: Implementación del patrón Observer
- `processes/`: Procesos específicos del negocio
- `workflows/`: Orquestación y coordinación de flujos

#### ui/

Interfaces de usuario para interacción:

- `login.py`: Diálogo gráfico para captura de credenciales
- Componentes Tkinter para entrada de datos del usuario

### Proceso de Login Obligatorio

Todo proceso debe implementar autenticación previa:

```python
class ProcesoEspecifico(BaseProcess):
    """
    Proceso específico que hereda funcionalidad base.

    Implementa el flujo completo de autenticación, navegación
    y ejecución de operaciones específicas del negocio.
    """

    def execute(self) -> bool:
        """
        Ejecuta el proceso completo con autenticación previa.

        Returns:
            bool: True si el proceso se ejecutó exitosamente.
        """
        try:
            # 1. Autenticación obligatoria
            if not self._perform_login():
                self.logger.error("Fallo en autenticación inicial")
                return False

            # 2. Navegación al módulo específico
            if not self._navigate_to_module():
                self.logger.error("Fallo en navegación al módulo")
                return False

            # 3. Ejecución del proceso específico
            if not self._execute_business_logic():
                self.logger.error("Fallo en lógica de negocio")
                return False

            # 4. Validación de resultados
            if not self._validate_result():
                self.logger.error("Fallo en validación de resultados")
                return False

            return True

        except Exception as e:
            self.logger.exception(f"Error crítico en proceso: {e}")
            return False
```

### Estructura de Manejo de Errores

Implementación obligatoria de recuperación con if not:

```python
def _execute_critical_operation(self) -> bool:
    """
    Ejecuta operación crítica con manejo de errores.

    Returns:
        bool: True si la operación fue exitosa.
    """
    try:
        # Operación principal
        result = self._perform_operation()

        # Validación inmediata
        if not result:
            self.logger.warning("Operación falló, intentando recuperación")

            # Estrategia de recuperación
            if not self._attempt_recovery():
                self.logger.error("Recuperación falló, terminando proceso")
                return False

        return True

    except Exception as e:
        self.logger.exception(f"Excepción en operación crítica: {e}")

        # Intento de recuperación ante excepción
        if not self._emergency_recovery():
            self.logger.critical("Recuperación de emergencia falló")
            return False

        return True
```

## Gestión de Excel

### Archivos de Entrada

#### entradas/ENTRADAS.xlsx

- Estructura predefinida con columnas específicas del proceso
- Validación automática de formato y contenido
- Procesamiento secuencial de registros

### Archivos de Salida

#### salidas/CONCILIACION.xlsx

- Registro de operaciones exitosas
- Timestamping automático de procesamiento
- Preservación de datos originales más metadatos

#### errores/ERRORES.xlsx

- Captura detallada de errores y excepciones
- Contexto completo del fallo para debugging
- Clasificación de errores por tipo y criticidad

## Documentación de Código

### Estándar Google Docstring

Todas las funciones deben documentarse según el estándar de Google:

```python
def procesar_registro(self, registro: dict, sesion_activa: bool = True) -> bool:
    """
    Procesa un registro individual del archivo de entrada.

    Ejecuta el flujo completo de procesamiento para un registro específico,
    incluyendo validación, transformación, ejecución web y registro de resultado.

    Args:
        registro: Diccionario con los datos del registro a procesar.
            Debe contener las claves requeridas según la configuración del proceso.
        sesion_activa: Indica si existe una sesión web activa.
            Si es False, se iniciará una nueva sesión antes del procesamiento.

    Returns:
        True si el registro se procesó exitosamente, False en caso contrario.

    Raises:
        ValueError: Si el registro no contiene las claves requeridas.
        ConnectionError: Si no se puede establecer conexión con el sistema web.
        TimeoutError: Si las operaciones web exceden el tiempo límite.

    Example:
        registro = {
            'numero_prestamo': '12345',
            'codigo_cargo': 'CF001',
            'fecha_efectiva': '20250123'
        }

        if procesar_registro(registro, sesion_activa=True):
            print("Registro procesado exitosamente")
    """
    pass
```

### Principios de Documentación

- **Claridad**: Explicación simple y directa de la funcionalidad
- **Completitud**: Documentación de todos los parámetros y valores de retorno
- **Ejemplos**: Casos de uso prácticos cuando sea relevante
- **Excepciones**: Documentación de errores posibles y su significado
- **Profesionalismo**: Lenguaje técnico preciso sin emojis ni coloquialismos

## Scripts de Configuración

### INSTALAR-CONFIGURAR.bat

Script para configuración automática del entorno:

```batch
@echo off
echo Configurando entorno Python para automatización RPA...

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en PATH
    pause
    exit /b 1
)

:: Instalar Poetry si no existe
pip show poetry >nul 2>&1
if errorlevel 1 (
    echo Instalando Poetry...
    pip install poetry
)

:: Configurar Poetry
echo Configurando Poetry para entorno local...
poetry config virtualenvs.create true
poetry config virtualenvs.in-project true

:: Instalar dependencias
echo Instalando dependencias del proyecto...
poetry install --no-root

echo Configuración completada exitosamente
pause
```

### EJECUTABLE.bat

Script para ejecución del sistema:

```batch
@echo off
echo Iniciando sistema de automatización RPA...

:: Verificar entorno virtual
if not exist ".venv" (
    echo ERROR: Entorno virtual no encontrado
    echo Ejecute INSTALAR-CONFIGURAR.bat primero
    pause
    exit /b 1
)

:: Activar entorno y ejecutar
call .venv\Scripts\activate.bat
python main.py

echo Proceso finalizado
pause
```

## Código Minimalista

### Principios de Optimización

- **Simplicidad**: Soluciones directas sin complejidad innecesaria
- **Eficiencia**: Uso óptimo de recursos de memoria y CPU
- **Legibilidad**: Código autodocumentado con nombres descriptivos
- **Mantenibilidad**: Estructura modular fácil de modificar y extender

### Estándares de Código

- Variables y funciones en snake_case
- Clases en PascalCase
- Constantes en UPPER_CASE
- Imports organizados según PEP 8
- Líneas máximo 88 caracteres (configuración Ruff)
- Type hints obligatorios en todas las funciones públicas

Esta estructura garantiza un sistema robusto, mantenible y escalable para cualquier proceso de automatización RPA.
