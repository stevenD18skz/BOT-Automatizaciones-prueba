@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ================================================
echo  BOT SIIF - CONSULTA DE CUENTAS DE AHORROS
echo ================================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No existe el entorno virtual .venv
    echo [SOLUCION] Ejecuta primero INSTALAR-CONFIGURAR.bat
    echo.
    pause
    exit /b 1
)

if not exist "entradas\ENTRADAS.xlsx" (
    echo [AVISO] No se encontro entradas\ENTRADAS.xlsx
    echo [CONTEXTO] El bot lo necesita para saber que cuentas consultar.
    echo            Debe tener las columnas INDEX y NUMERO_CUENTA.
    echo.
    echo Puedes iniciar igual y cargarlo antes de pulsar "Ejecutar proceso".
    echo.
    pause
)

echo [INFO] Arrancando el Bot y la interfaz...
echo [INFO] Se abrira una ventana aparte con el log del Bot.
echo [INFO] Para cerrar todo: Ctrl+C aqui y cierra la ventana del Bot.
echo.

".venv\Scripts\python.exe" main.py

echo.
echo Proceso finalizado.
pause
