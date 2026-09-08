# Comandos del proyecto

Chuleta de todos los comandos del Bot SIIF. Todo se ejecuta desde la raíz del proyecto:

```powershell
cd C:\Users\brayan.narvaez\Desktop\BOT-Automatizaciones-prueba
```

> **Truco:** en todos los comandos se usa `.venv\Scripts\python.exe` en vez de activar el entorno.
> Así funciona siempre, sin depender de si activaste el `.venv` o no.

---

## 1. Instalación

### Automática (recomendada)

Doble clic en `INSTALAR-CONFIGURAR.bat`, o desde terminal:

```powershell
.\INSTALAR-CONFIGURAR.bat
```

Verifica Python 3.13+, instala Poetry si falta, crea el `.venv` dentro del proyecto e instala dependencias.

### Manual

```powershell
python --version                          # confirmar 3.13 o superior
pip install poetry
poetry config virtualenvs.in-project true
poetry install --no-root
```

### Agregar una dependencia nueva

```powershell
poetry add nombre-del-paquete
```

---

## 2. Arranque

### Todo de una vez (lo normal)

```powershell
.venv\Scripts\python.exe main.py
```

Levanta el Bot en una ventana de consola aparte y abre la UI en el navegador.

O doble clic en **`EJECUTAR.bat`**, que hace lo mismo y avisa si falta algo.

### Por separado (para depurar)

Útil cuando quieres ver los errores de cada lado sin que se mezclen. Dos terminales:

```powershell
# Terminal 1 — el Bot
.venv\Scripts\python.exe -m bot.server
```

```powershell
# Terminal 2 — la UI
.venv\Scripts\python.exe -m streamlit run client\app.py --server.port=8501
```

---

## 3. Puertos

| Servicio | Puerto | URL |
|---|---|---|
| UI (Streamlit) | **8501** | http://127.0.0.1:8501 |
| Bot (WebSocket) | **8765** | ws://127.0.0.1:8765 |

Se configuran en `config/settings.py` (`UI_PORT` y `BOT_PORT`).

> Si tienes `credioro-app` corriendo, ocupa **estos mismos puertos**. No pueden estar los dos
> a la vez: cierra uno, o cambia los puertos de este proyecto en `config/settings.py`.

---

## 4. Ver el estado

```powershell
# ¿Están arriba el Bot y la UI?
Get-NetTCPConnection -LocalPort 8765,8501 -State Listen -ErrorAction SilentlyContinue | Select-Object LocalPort, OwningProcess
```

```powershell
# Procesos de este proyecto
Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like '*BOT-Automatizaciones-prueba*' } | Select-Object ProcessId, CommandLine
```

```powershell
# ¿Quién ocupa un puerto? (cambia el número)
$c = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue
foreach ($x in $c) { (Get-CimInstance Win32_Process -Filter "ProcessId=$($x.OwningProcess)").CommandLine }
```

```powershell
# ¿SIIF es alcanzable? (ojo: es IP interna, requiere red del banco)
(Test-NetConnection siif.girosyfinanzas.com -Port 80 -WarningAction SilentlyContinue).TcpTestSucceeded
```

---

## 5. Detener y limpiar

```powershell
# Matar SOLO los procesos de este proyecto (no toca credioro-app)
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -like '*BOT-Automatizaciones-prueba*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

> **Cuidado:** ese filtro busca la ruta del proyecto en la línea de comandos. Si arrancaste
> con ruta relativa (`streamlit run client/app.py`), la ruta **no aparece** y el proceso
> sobrevive — luego el nuevo no puede tomar el puerto y sigues viendo código viejo.

Matar por puerto es infalible, porque no depende de cómo lo lanzaste:

```powershell
# Cambia 8501 por 8765 para el Bot. Mata el proceso y su padre.
$owner = (Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue).OwningProcess
$todos = @()
foreach ($o in $owner) {
  $todos += $o
  $todos += (Get-CimInstance Win32_Process -Filter "ProcessId=$o").ParentProcessId
}
if ($todos) { Stop-Process -Id ($todos | Sort-Object -Unique) -Force -ErrorAction SilentlyContinue }
```

```powershell
# Matar Chrome huérfano dejado por el bot (NO toca tu Chrome normal)
$p = (Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" |
      Where-Object { $_.CommandLine -like '*rpa_chrome_*' }).ProcessId
if ($p) { Stop-Process -Id $p -Force }
Get-Process chromedriver -ErrorAction SilentlyContinue | Stop-Process -Force
```

> Los perfiles de Chrome del bot se llaman `rpa_chrome_*` y son temporales: uno nuevo por
> ejecución, y se borra solo al cerrar. Por eso filtrar por ese nombre nunca afecta a tu navegador.

---

## 6. Logs

```powershell
# Seguir el log en vivo (como tail -f)
Get-Content logs\rpa.log -Wait -Tail 30
```

```powershell
# Solo los errores
Select-String -Path logs\rpa.log -Pattern "ERROR" | Select-Object -Last 20
```

```powershell
# Empezar de cero
Remove-Item logs\rpa.log
```

---

## 7. Probar el WebSocket a mano

### Con Bruno

*New Request* → tipo **WebSocket** → `ws://127.0.0.1:8765` → **Connect**.

Al conectar ya recibes un evento sin pedir nada. Mensajes que puedes enviar:

```json
{ "type": "command", "version": 1, "id": "1", "cmd": "ping",   "payload": {} }
{ "type": "command", "version": 1, "id": "2", "cmd": "status", "payload": {} }
{ "type": "command", "version": 1, "id": "3", "cmd": "execute","payload": {} }
{ "type": "command", "version": 1, "id": "4", "cmd": "stop",   "payload": {} }
{ "type": "command", "version": 1, "id": "5", "cmd": "logout", "payload": {} }
{ "type": "command", "version": 1, "id": "6", "cmd": "login",  "payload": { "username": "USUARIO", "password": "CLAVE" } }
{ "type": "command", "version": 1, "id": "7", "cmd": "demo",   "payload": { "registros": 20, "pausa": 1.0 } }
```

> `demo` recorre un lote falso emitiendo los mismos eventos que una corrida real, sin abrir
> Chrome ni tocar SIIF. Sirve para probar la UI y el WebSocket sin credenciales.

> No dejes tu contraseña guardada en los archivos `.bru` de la colección.

### Desde la consola del navegador (F12)

```js
const ws = new WebSocket("ws://127.0.0.1:8765");
ws.onmessage = e => console.log(JSON.parse(e.data));
ws.onopen = () => ws.send(JSON.stringify({
  type: "command", version: 1, id: "1", cmd: "ping", payload: {}
}));
```

En **DevTools → Network → filtro WS** puedes ver las tramas entrando y saliendo en vivo.

### Desde terminal

```powershell
npm install -g wscat
wscat -c ws://127.0.0.1:8765
```

---

## 8. Git

```powershell
git status
git add .
git commit -m "mensaje"
git push origin main
git log --oneline -10
```

---

## 9. Problemas frecuentes

| Síntoma | Causa y solución |
|---|---|
| `ERR_CONNECTION_REFUSED` al hacer login | SIIF está en una IP interna (`10.122.5.5`). Parpadeo de red o VPN caída. Reintenta; si persiste, revisa la VPN. |
| `DevToolsActivePort file doesn't exist` | Quedó Chrome huérfano bloqueando el perfil. Usa la limpieza de la sección 5. |
| El Bot escucha pero no responde nada | Hiciste clic dentro de su ventana de consola y Windows la puso en modo selección, congelando la salida. Pulsa `Esc` o `Enter` dentro de esa ventana. |
| El puerto ya está en uso | Lo tiene `credioro-app` (usa los mismos) o quedó un proceso viejo. Sección 4 para ver quién, sección 5 para matarlo. |
| La UI dice "Sin conexión con el Bot" | El Bot no está arriba. Levántalo con `.venv\Scripts\python.exe -m bot.server`; la UI se reconecta sola. |
| `no workbook found ... ENTRADAS.xlsx` | Falta `entradas\ENTRADAS.xlsx` con las columnas `INDEX` y `NUMERO_CUENTA`. |
