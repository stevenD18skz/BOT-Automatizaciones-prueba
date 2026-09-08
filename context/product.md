# Bot Vinculación Clientes

## Descripción

Sistema de automatización RPA para la vinculación de clientes en SIIF.

## Características Principales

### Funcionalidades Core

- **Procesamiento por Lotes**: Manejo automático de múltiples registros desde Excel
- **Sesión Independiente**: Login automático por cada registro procesado
- **Validación de Resultados**: Verificación automática del éxito de cada operación
- **Manejo de Errores**: Captura y registro detallado de errores en archivos separados
- **Trazabilidad Completa**: Registro de todas las operaciones exitosas y fallidas

### Gestión de Datos

- **Entrada**: Archivo Excel con estructura predefinida (ENTRADAS.xlsx)
- **Salida Exitosa**: Consolidado de registros procesados correctamente (CONCILIACION.xlsx)
- **Salida de Errores**: Registro detallado de fallos y causas (ERRORES.xlsx)
- **Actualización Automática**: Eliminación de registros procesados del archivo de entrada

### Robustez y Confiabilidad

- **Recuperación de Errores**: Continuidad del proceso ante fallos individuales
- **Validación de Credenciales**: Interface gráfica para captura segura de usuario y contraseña
- **Logging Detallado**: Registro completo de todas las operaciones del sistema
- **Configuración Centralizada**: Gestión de parámetros desde archivo de configuración único

## Requisitos del Sistema

### Software Base

- **Python**: 3.13.x o superior
- **Sistema Operativo**: Windows 10/11 (recomendado)
- **Navegador**: Google Chrome (actualizado)
- **Conectividad**: Acceso a red para SIIF

### Dependencias Técnicas

- **Poetry**: Gestor de dependencias y entornos virtuales
- **Selenium**: Automatización de navegador web
- **Polars**: Procesamiento eficiente de datos
- **Tkinter**: Interface gráfica para credenciales (incluido en Python)

## Instalación

### Instalación Automática

1. Ejecutar el archivo `INSTALAR-CONFIGURAR.bat`
2. Seguir las instrucciones en pantalla
3. El sistema configurará automáticamente el entorno virtual y las dependencias

### Instalación Manual

```bash
# Verificar Python
python --version

# Instalar Poetry
pip install poetry

# Configurar Poetry
poetry config virtualenvs.in-project true
poetry config virtualenvs.create true

# Instalar dependencias
poetry install --no-root
```

## Configuración

### Archivo de Configuración

El sistema utiliza `config/settings.py` para la configuración centralizada:

```python
# URL del sistema SIIF
SIIF_URL = "http://siif.girosyfinanzas.com/BUN_V12/"

# Rutas de archivos
INPUT_FILE_PATH = "entradas/ENTRADAS.xlsx"
OUTPUT_FILE_PATH = "salidas/CONCILIACION.xlsx"
ERROR_FILE_PATH = "errores/ERRORES.xlsx"
```

### Estructura de Datos de Entrada

El archivo `ENTRADAS.xlsx` debe contener las siguientes columnas:

| Columna | Descripción | Tipo | Requerido |
|---------|-------------|------|-----------|

## Uso

### Ejecución Automática

```bash
# Desde la raíz del proyecto
EJECUTABLE.bat
```

### Ejecución Manual

```bash
# Activar entorno virtual
.venv\Scripts\activate

# Ejecutar aplicación
python main.py
```

### Flujo de Operación

1. **Inicio**: El sistema solicita credenciales mediante interface gráfica
2. **Carga de Datos**: Lee automáticamente el archivo de entrada
3. **Procesamiento**: Para cada registro ejecuta:
   - Navegación a SIIF
   - Autenticación con credenciales
   - Validación de existencia del cliente:
     - Navegar a: Menú Principal / Sistema de clientes / Consulta de clientes
     - Digitar Tipo de Identificación y Número de identificación
     - Verificar si el cliente existe en el sistema
   - Si el cliente NO existe, proceder con la vinculación:
     - Navegar a: SIIF / Iniciación de Clientes / Vinculación de Captaciones
     - Digitar tipo de identificación y número de identificación del cliente
     - Configurar Producto de Captaciones = 3
     - Configurar Captura automática = 2
     - Completar todos los campos obligatorios (*) según datos del Excel
     - Enviar y confirmar la creación
   - Validación del resultado de la operación
4. **Consolidación**: Genera archivos de salida y actualiza entradas

## Archivos de Salida

### CONCILIACION.xlsx

Contiene todos los registros procesados exitosamente con:

- Fecha y hora de procesamiento
- Datos originales del registro
- Mensaje de confirmación del sistema

### ERRORES.xlsx

Registra todos los fallos ocurridos durante el procesamiento:

- Fecha y hora del error
- Datos del registro que falló
- Descripción detallada del error
- Contexto de la falla

## Mantenimiento

### Logs del Sistema

Los logs detallados se almacenan en `logs/rpa.log` con información de:

- Operaciones ejecutadas
- Errores y excepciones
- Tiempos de ejecución
- Estado de las sesiones

### Actualización de Dependencias

```bash
# Actualizar todas las dependencias
poetry update

# Actualizar dependencia específica
poetry add selenium@latest
```

## Soporte Técnico

### Problemas Comunes

- **Error de Credenciales**: Verificar usuario y contraseña en SIIF
- **Timeout de Sesión**: El sistema maneja automáticamente renovación de sesión
- **Archivo No Encontrado**: Verificar ubicación de ENTRADAS.xlsx
- **Problemas de Red**: Verificar conectividad con servidor SIIF

### Contacto

Para soporte técnico o reportes de errores, contactar al equipo de desarrollo con:

- Archivos de log relevantes
- Descripción detallada del problema
- Pasos para reproducir el error

## Versionado

Este proyecto sigue el estándar de versionado semántico (SemVer):

- **MAJOR**: Cambios incompatibles en la API
- **MINOR**: Nuevas funcionalidades compatibles
- **PATCH**: Correcciones de errores

Versión actual: Consultar archivo `pyproject.toml`
