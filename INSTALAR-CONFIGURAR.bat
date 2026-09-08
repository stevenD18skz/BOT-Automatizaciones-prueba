@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================
echo  INSTALACION Y CONFIGURACION DEL PROYECTO RPA
echo ================================================
echo.

:: Variables del proyecto
set PYTHON_REQUIRED_VERSION=3.13

echo [CONTEXTO] Iniciando proceso de instalacion y configuracion del entorno de desarrollo
echo [1/4] Verificando version global de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH
    echo [CONTEXTO] El sistema requiere Python para ejecutar el proyecto RPA
    echo.
    echo [SOLUCION] Por favor instala Python desde: https://www.python.org/downloads/
    echo [IMPORTANTE] Asegurate de marcar "Add Python to PATH" durante la instalacion
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python encontrado: version %PYTHON_VERSION%

:: Verificar si la versión es compatible
for /f "tokens=1,2,3 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
    set PATCH=%%c
)

if %MAJOR% lss 3 (
    echo [ERROR] Se requiere Python %PYTHON_REQUIRED_VERSION% o superior. Version actual: %PYTHON_VERSION%
    echo [CONTEXTO] Esta version de Python no es compatible con las dependencias del proyecto
    pause
    exit /b 1
)

if %MAJOR% equ 3 if %MINOR% lss 13 (
    echo [ERROR] Se requiere Python %PYTHON_REQUIRED_VERSION% o superior. Version actual: %PYTHON_VERSION%
    echo [CONTEXTO] Las dependencias del proyecto requieren caracteristicas disponibles desde Python 3.13
    pause
    exit /b 1
)

echo.
echo [2/4] Verificando instalacion de poetry...
echo [CONTEXTO] Poetry es el gestor de dependencias utilizado en este proyecto
poetry --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Poetry no encontrado. Procediendo con la instalacion...
    echo [CONTEXTO] Instalando poetry para gestionar las dependencias del proyecto
    echo.
    python -m pip install --upgrade pip
    python -m pip install poetry
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo instalar poetry
        echo [CONTEXTO] Poetry es necesario para gestionar las dependencias del proyecto
        pause
        exit /b 1
    )
    echo [OK] Poetry instalado correctamente
) else (
    for /f "tokens=2" %%i in ('poetry --version 2^>^&1') do set POETRY_VERSION=%%i
    echo [OK] Poetry encontrado: version !POETRY_VERSION!
)

echo.
echo [CONTEXTO] Configurando poetry para crear entornos virtuales en el proyecto...
poetry config virtualenvs.create true
if %errorlevel% neq 0 (
    echo [WARNING] No se pudo habilitar la creacion de entornos virtuales
) else (
    echo [OK] Creacion de entornos virtuales habilitada
)

poetry config virtualenvs.in-project true
if %errorlevel% neq 0 (
    echo [WARNING] No se pudo configurar virtualenvs.in-project
) else (
    echo [OK] Entorno virtual se creara en el directorio del proyecto (.venv)
)

echo.
echo [3/4] Configurando entorno virtual...
echo [CONTEXTO] Creando entorno virtual aislado para las dependencias del proyecto
if exist ".venv" (
    echo [INFO] Entorno virtual existente encontrado. Eliminando para instalacion limpia...
    rmdir /s /q ".venv"
)


echo [CONTEXTO] Instalando dependencias del proyecto desde pyproject.toml...
poetry install --no-root
if %errorlevel% neq 0 (
    echo [ERROR] No se pudieron instalar las dependencias
    echo [CONTEXTO] Verifica la conectividad a internet y que el archivo pyproject.toml sea valido
    pause
    exit /b 1
)

echo.
echo [4/4] Verificando instalacion...
echo [CONTEXTO] Validando que el entorno virtual y las dependencias se instalaron correctamente
if exist ".venv\Scripts\python.exe" (
    echo [OK] Entorno virtual creado correctamente
    .venv\Scripts\python.exe --version
    echo [OK] Dependencias instaladas correctamente
) else (
    echo [ERROR] El entorno virtual no se creo correctamente
    echo [CONTEXTO] Verifica que hay espacio suficiente en disco y permisos de escritura
    pause
    exit /b 1
)

echo.
echo ================================================
echo [EXITO] INSTALACION COMPLETADA CON EXITO
echo ================================================
echo.
echo [CONTEXTO] El proyecto esta listo para usar.
echo [INFO] Version de Python configurada: %PYTHON_REQUIRED_VERSION% o superior
echo [INFO] Version de Python detectada: %PYTHON_VERSION%
echo.
echo [INSTRUCCIONES] Para ejecutar el proyecto:
echo   1. Activa el entorno virtual: .venv\Scripts\activate
echo   2. Ejecuta el programa: python main.py
echo   3. O ejecuta "EJECUTABLE.bat" en el directorio principal del proyecto
echo.
echo [ALTERNATIVA] Tambien puedes ejecutar: poetry run python main.py
echo.
echo ================================================
pause
