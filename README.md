# Bot Plantilla Automatización RPA

Bot de RPA (automatización robótica de procesos) construido en Python + Selenium para operar sobre **SIIF** (`http://siif.girosyfinanzas.com/BUN_V12/`), un sistema web interno del negocio. Nace como plantilla de la Célula de Mejora Operativa: la estructura está pensada para reutilizarse en distintos procesos SIIF, y la instancia actual implementa el proceso **"Consulta de Cuentas de Ahorros"**.

## ¿Por qué existe este repo?

Antes, cada consulta de cuenta en SIIF se hacía manualmente en el navegador, una por una. Este proyecto automatiza ese flujo: toma un lote de números de cuenta desde un Excel, se loguea en SIIF una sola vez, navega al módulo de consulta y busca cada cuenta, y deja como resultado dos Excel (uno con lo que salió bien, otro con lo que falló y por qué).

Además, la UI y el bot corren en **procesos separados que se hablan por WebSocket**. Eso resuelve dos problemas del enfoque anterior (un solo script con ventana de Tkinter): la interfaz ya no se congela mientras Selenium trabaja, y el bot puede **empujar el avance en vivo** a la UI (cuenta 3 de 50, esta falló, etc.) sin que la UI tenga que estar preguntando.

## Arquitectura

```text
Streamlit (cliente)  ──WebSocket/JSON──►  Bot (servidor)
  client/app.py                             bot/server.py
  client/ipc.py                             bot/session.py
        │                                        │
        └────────── protocol.py (contrato compartido) ──────────┘
```

Son **dos procesos de Python independientes**. Streamlit nunca toca Selenium: todo pasa por el socket.

**Servidor** (`bot/server.py`) — escucha en `ws://127.0.0.1:8766`. Como Selenium es bloqueante, el trabajo pesado sale del event loop: `login`/`logout` corren en un hilo (`asyncio.to_thread`) y responden al terminar; `execute` arranca un hilo propio y responde *"iniciado"* de inmediato. `ping`, `status` y `stop` se atienden siempre, incluso con un lote corriendo, para que la UI nunca se quede muda.

**Cliente** (`client/ipc.py`) — a diferencia de un socket TCP de petición/respuesta, mantiene **una sola conexión abierta** en un hilo de fondo. Por ahí salen los comandos y por ahí entran tanto las respuestas (correlacionadas por `id`) como los eventos que el Bot empuja solo. El hilo nunca toca la API de Streamlit: escribe en estructuras propias que la UI lee en cada refresco.

**Protocolo** (`protocol.py`) — el "idioma" compartido. Tres tipos de mensaje:

| Tipo | Dirección | Para qué |
|---|---|---|
| `command` | cliente → servidor | "haz esto" (lleva un `id`) |
| `response` | servidor → cliente | resultado de ese `id` |
| `event` | servidor → cliente | "esto está pasando" — **nadie lo pidió** |

Comandos: `ping`, `status`, `login`, `logout`, `execute`, `stop`.
Eventos: `log`, `state`, `run_started`, `progress`, `record`, `run_finished`.

Los eventos son la razón de usar WebSocket: con un socket TCP clásico la UI tendría que preguntar "¿cómo vas?" en bucle.

## Qué hace, paso a paso

1. Abres la UI y escribes tus credenciales de SIIF — **no se guardan en ningún archivo**.
2. El Bot abre Chrome (Selenium + `webdriver-manager`, que baja el driver correcto solo), navega a SIIF y hace login. La sesión queda abierta.
3. Pulsas *Ejecutar*: el Bot lee `entradas/ENTRADAS.xlsx` con Polars y recorre los registros.
4. Por cada fila navega al módulo de consulta y busca el `NUMERO_CUENTA`, emitiendo eventos de progreso que la UI pinta en vivo (barra, métricas, tabla, consola).
5. Cada `BATCH_SIZE` (100) registros procesados, limpia lo ya hecho de `ENTRADAS.xlsx`.
6. Puedes pulsar *Detener* en cualquier momento: termina el registro actual y corta limpio.
7. Al terminar escribe `salidas/CONCILIACION.xlsx` (éxitos) y `errores/ERRORES.xlsx` (fallos). Todo queda además en `logs/rpa.log`.

## Estructura del proyecto

```text
protocol.py              Contrato compartido cliente/servidor
bot/
  server.py              Servidor WebSocket (punto de entrada del Bot)
  session.py             Estado vivo: navegador, sesión SIIF, corrida en curso
client/
  app.py                 UI de Streamlit
  ipc.py                 Cliente WebSocket + autoarranque del Bot
config/                  Configuración centralizada (URL, rutas, puerto, batch)
core/                    Framework RPA reutilizable (driver, esperas, proceso base)
services/
  data/                  Lectura/escritura de los Excel
  navigation/            Navegación por menús de SIIF
  processes/             Procesos de negocio (login, búsqueda de cuenta)
  workflows/             Orquestador del lote (emite eventos, soporta detención)
context/                 Documentación de referencia de la plantilla
main.py                  Lanzador: levanta Bot + UI de una sola vez
```

## Requisitos

- Python 3.13 o superior
- Windows 10/11 (recomendado)
- Google Chrome instalado
- Acceso de red al servidor de SIIF
- [Poetry](https://python-poetry.org/) (se instala solo con el script automático)

## Instalación

### Opción 1: automática (recomendada)

Ejecuta `INSTALAR-CONFIGURAR.bat`. Verifica la versión de Python, instala Poetry si falta, crea el entorno virtual dentro del proyecto (`.venv`) e instala las dependencias.

### Opción 2: manual

```bash
python --version          # confirmar 3.13+
pip install poetry
poetry config virtualenvs.in-project true
poetry install --no-root
```

## Configuración

Crea la carpeta de entrada (está ignorada en git porque lleva datos reales):

```text
entradas/ENTRADAS.xlsx
```

Debe tener al menos estas columnas:

| Columna | Descripción |
|---|---|
| `INDEX` | Identificador único de la fila (se usa para depurar el Excel tras procesar) |
| `NUMERO_CUENTA` | Número de cuenta de ahorros a consultar en SIIF |

`salidas/` y `errores/` se generan solos al terminar.

Los parámetros generales (URL de SIIF, rutas, puerto del WebSocket, tamaño de lote) están en `config/settings.py`.

> El puerto es **8766** y no 8765 para no chocar con el bot de `credioro_app` si ambos corren en la misma máquina.

## Uso

```bash
.venv\Scripts\activate
python main.py
```

`main.py` levanta el Bot en su propia ventana de consola (ahí ves el flujo de eventos en vivo) y abre la UI de Streamlit en el navegador.

Para depurar, puedes arrancarlos por separado en dos terminales:

```bash
python -m bot.server            # servidor
streamlit run client/app.py     # UI
```

Al terminar, revisa `salidas/CONCILIACION.xlsx`, `errores/ERRORES.xlsx` y `logs/rpa.log`.

## Notas de seguridad

- Las credenciales de SIIF se piden en cada ejecución por la UI y nunca se persisten en disco ni en el repo.
- El WebSocket escucha solo en `127.0.0.1`, y Streamlit está configurado en `.streamlit/config.toml` para no exponerse a la red.
- `entradas/`, `salidas/`, `errores/` y `logs/` están en `.gitignore`: contienen números de cuenta y otra información sensible del negocio.
