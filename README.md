# Bot Plantilla Automatización RPA

Bot de RPA (automatización robótica de procesos) construido en Python + Selenium para operar sobre **SIIF** (`http://siif.girosyfinanzas.com/BUN_V12/`), un sistema web interno del negocio. Nace como plantilla de la Célula de Mejora Operativa: la estructura (`core/`, `services/`, `ui/`) está pensada para reutilizarse en distintos procesos SIIF, y la instancia actual del repo implementa el proceso **"Consulta de Cuentas de Ahorros"**.

## ¿Por qué existe este repo?

Antes de este bot, cada consulta/verificación de cuenta en SIIF se hacía manualmente en el navegador, una por una. Este proyecto automatiza ese flujo: toma un lote de números de cuenta desde un Excel, se loguea en SIIF una sola vez, navega al módulo de consulta y busca cada cuenta, y deja como resultado dos Excel (uno con lo que salió bien, otro con lo que falló y por qué). La arquitectura (`core/`) está separada del proceso de negocio (`services/processes/search_account_name.py`) justamente para que agregar un nuevo proceso SIIF a futuro sea cuestión de escribir una clase nueva, no de reescribir el framework.

## Qué hace, paso a paso

1. Al arrancar, pide usuario y contraseña de SIIF por una ventana (Tkinter) — **no se guardan en ningún archivo**.
2. Abre Chrome (vía Selenium + `webdriver-manager`, que descarga el driver correcto automáticamente) y navega a la URL de SIIF.
3. Hace login una sola vez.
4. Lee `entradas/ENTRADAS.xlsx` con Polars.
5. Por cada fila: navega al módulo de consulta de cuentas y busca el número de cuenta (`NUMERO_CUENTA`).
6. Cada resultado se clasifica como éxito o error y se va acumulando; cada `BATCH_SIZE` (100) registros procesados, se limpia lo ya procesado de `ENTRADAS.xlsx`.
7. Al terminar, escribe:
   - `salidas/CONCILIACION.xlsx` → registros procesados con éxito.
   - `errores/ERRORES.xlsx` → registros que fallaron, con el mensaje de error.
8. Todo el proceso queda registrado en `logs/rpa.log`.

## Estructura del proyecto

```text
config/                  Configuración centralizada (URL SIIF, rutas, batch size, menú)
core/                    Framework RPA reutilizable (driver, esperas, clase base de proceso)
services/
  data/                  Lectura/escritura de los Excel de entrada y salida
  navigation/            Navegación por menús de SIIF
  processes/             Procesos de negocio (login, búsqueda de cuenta)
  workflows/             Orquestador: conecta todo lo anterior
ui/                      Ventana de login (Tkinter)
context/                 Documentación de referencia de la plantilla (arquitectura, convenciones)
main.py                  Punto de entrada
```

## Requisitos

- Python 3.13 o superior
- Windows 10/11 (recomendado; usa rutas y `.bat` de Windows)
- Google Chrome instalado
- Acceso de red al servidor de SIIF
- [Poetry](https://python-poetry.org/) (se instala solo si usas el script automático)

## Instalación

### Opción 1: automática (recomendada)

Ejecuta `INSTALAR-CONFIGURAR.bat` y sigue las instrucciones en pantalla. El script verifica la versión de Python, instala Poetry si hace falta, configura el entorno virtual dentro del proyecto (`.venv`) e instala las dependencias.

### Opción 2: manual

```bash
python --version          # confirmar 3.13+
pip install poetry
poetry config virtualenvs.in-project true
poetry config virtualenvs.create true
poetry install --no-root
```

## Configuración

Antes de correr el bot, crea estas carpetas si no existen (están ignoradas en git porque contienen datos reales de cuentas):

```text
entradas/ENTRADAS.xlsx
salidas/            (se genera solo al terminar)
errores/            (se genera solo al terminar)
```

`entradas/ENTRADAS.xlsx` debe tener, como mínimo, las columnas:

| Columna | Descripción |
|---|---|
| `INDEX` | Identificador único de la fila (se usa para depurar el Excel tras procesar) |
| `NUMERO_CUENTA` | Número de cuenta de ahorros a consultar en SIIF |

Los parámetros generales (URL de SIIF, rutas de archivos, tamaño de lote, ruta de menú) están centralizados en `config/settings.py` — no hace falta tocar código para ajustarlos.

## Uso

```bash
# Con el entorno virtual activo
.venv\Scripts\activate
python main.py
```

Se abrirá primero la ventana de login; una vez ingreses tus credenciales de SIIF, el bot abre Chrome y procesa el archivo de entrada automáticamente. Al finalizar revisa `salidas/CONCILIACION.xlsx`, `errores/ERRORES.xlsx` y `logs/rpa.log`.

## Notas de seguridad

- Las credenciales de SIIF se piden en cada ejecución por UI y nunca se persisten en disco ni en el repo.
- `entradas/`, `salidas/`, `errores/` y `logs/` están en `.gitignore`: pueden contener números de cuenta y otra información sensible del negocio, así que no deben commitearse.
