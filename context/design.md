# Diseño del Sistema RPA

## Introducción

Este documento describe la arquitectura y diseño del sistema de automatización RPA basado en el módulo core desarrollado para la automatización de procesos web. El sistema está diseñado para ser modular, extensible y robusto, permitiendo la creación de bots especializados para diferentes procesos de negocio.

## Arquitectura del Core RPA

### Principios de Diseño

El módulo core está fundamentado en los siguientes principios arquitectónicos:

- **Modularidad**: Cada componente tiene una responsabilidad específica y bien definida
- **Extensibilidad**: Fácil incorporación de nuevos procesos y funcionalidades
- **Robustez**: Manejo integral de errores y recuperación automática
- **Configurabilidad**: Parámetros centralizados y fácilmente modificables
- **Trazabilidad**: Registro completo de todas las operaciones y estados

### Componentes Fundamentales

#### Base Process (BaseProcess)

Clase abstracta que define la estructura común para todos los procesos RPA:

```python
class BaseProcess:
    """
    Clase base para todos los procesos de automatización.

    Proporciona la estructura común y métodos fundamentales que deben
    implementar todos los procesos específicos del sistema.
    """

    def execute(self) -> bool:
        """Método principal que ejecuta el proceso completo."""
        pass

    def _validate_result(self) -> bool:
        """Valida si el proceso se ejecutó correctamente."""
        pass
```

#### Driver Manager

Gestiona la configuración y ciclo de vida del navegador web:

- Configuración automática de ChromeDriver
- Gestión de opciones del navegador
- Control de timeouts y esperas
- Limpieza automática de recursos

#### Navigator

Coordinador de navegación que maneja:

- Navegación entre módulos del sistema
- Gestión de menús y submenús
- Validación de rutas de navegación
- Manejo de estados de sesión

#### Data Manager

Controlador de entrada y salida de datos:

- Lectura de archivos Excel de entrada
- Transformación de datos para procesamiento
- Generación de archivos de salida
- Actualización automática de archivos de entrada

## Patrones de Diseño Implementados

### Observer Pattern

Implementado en los observadores de éxito y error:

```python
class ErrorObserver:
    """
    Observador especializado en el registro inmediato de errores.

    Garantiza la persistencia de errores críticos mediante escritura
    inmediata a archivo, evitando pérdida de información en caso
    de fallas del sistema.
    """

    def update(self, data: dict) -> None:
        """Registra inmediatamente el error en el archivo correspondiente."""
        pass
```

### Template Method Pattern

La clase BaseProcess implementa este patrón:

- Define el flujo general de ejecución
- Permite especialización en subclases
- Garantiza consistencia en la estructura de procesos

### Factory Pattern

El DriverManager utiliza este patrón para:

- Crear instancias de navegador según configuración
- Aplicar configuraciones específicas por tipo de proceso
- Gestionar diferentes tipos de drivers web

## Arquitectura por Capas

### Capa de Presentación (UI)

- **Componentes**: Diálogos de entrada de credenciales
- **Responsabilidad**: Captura de datos del usuario
- **Tecnología**: Tkinter para interfaces nativas

### Capa de Orquestación (Workflows)

- **Componentes**: Orchestrator, coordinadores de flujo
- **Responsabilidad**: Control de flujo de procesos
- **Funciones**: Gestión de sesiones, control de lotes

### Capa de Servicios (Services)

- **Componentes**: Procesos específicos, navegadores, gestores de datos
- **Responsabilidad**: Lógica de negocio y operaciones especializadas
- **Especialización**: Un servicio por tipo de proceso

### Capa de Core (Core)

- **Componentes**: Clases base, interfaces, utilidades
- **Responsabilidad**: Funcionalidad común y abstracciones
- **Estabilidad**: Componentes de bajo cambio y alta reutilización

### Capa de Configuración (Config)

- **Componentes**: Settings, constantes, parámetros
- **Responsabilidad**: Configuración centralizada del sistema
- **Mantenimiento**: Punto único de configuración

## Flujo de Datos

### Entrada de Datos

1. **Lectura**: El DataManager lee el archivo Excel de entrada
2. **Validación**: Se verifican las columnas requeridas y formatos
3. **Transformación**: Los datos se convierten al formato interno
4. **Distribución**: Los registros se distribuyen para procesamiento

### Procesamiento

1. **Inicialización**: Se crea una nueva sesión de navegador
2. **Autenticación**: Login automático con credenciales del usuario
3. **Navegación**: Acceso al módulo específico del proceso
4. **Ejecución**: Realización de las operaciones del proceso
5. **Validación**: Verificación del resultado de la operación

### Salida de Datos

1. **Clasificación**: Los resultados se clasifican como éxito o error
2. **Registro**: Se actualizan los archivos de salida correspondientes
3. **Actualización**: Se elimina el registro procesado de la entrada
4. **Notificación**: Los observadores registran el estado final

## Gestión de Errores

### Estrategia de Recuperación

El sistema implementa múltiples niveles de recuperación:

#### Nivel de Proceso

- Reintentos automáticos en operaciones críticas
- Validación de estados intermedios
- Rollback automático en caso de falla

#### Nivel de Sesión

- Renovación automática de sesiones expiradas
- Login independiente por cada registro
- Gestión de timeouts de navegador

#### Nivel de Datos

- Preservación de datos ante fallas
- Escritura inmediata de errores críticos
- Continuidad del proceso ante registros defectuosos

### Clasificación de Errores

Los errores se clasifican según su criticidad:

- **Críticos**: Detienen el proceso completo
- **Recuperables**: Permiten continuar con el siguiente registro
- **Informativos**: No afectan la ejecución pero se registran

## Configuración y Personalización

### Archivo de Configuración Central

El sistema utiliza un archivo `settings.py` centralizado que define:

```python
# Configuración de URLs y endpoints
SIIF_URL = "http://sistema.ejemplo.com"

# Rutas de archivos de datos
INPUT_FILE_PATH = "entradas/ENTRADAS.xlsx"
OUTPUT_FILE_PATH = "salidas/CONCILIACION.xlsx"
ERROR_FILE_PATH = "errores/ERRORES.xlsx"

# Configuración de navegación
MENU_ROUTE = {
    "menu": "Sistema Principal",
    "submenu": "Proceso Específico",
    "processes": {...}
}
```

### Parametrización por Proceso

Cada proceso puede definir sus propios parámetros específicos:

- Timeouts personalizados
- Selectores CSS específicos
- Validaciones particulares
- Formatos de datos especializados

## Extensibilidad del Sistema

### Creación de Nuevos Procesos

Para crear un nuevo proceso RPA:

1. **Heredar de BaseProcess**: Implementar la clase base
2. **Definir execute()**: Implementar la lógica específica del proceso
3. **Configurar navegación**: Añadir rutas en settings.py
4. **Integrar observadores**: Conectar con el sistema de registro
5. **Configurar orquestador**: Añadir al flujo principal

### Extensión de Funcionalidades

El sistema permite extensión mediante:

- **Nuevos observers**: Para diferentes tipos de notificación
- **Utilidades específicas**: Helpers para operaciones comunes
- **Validadores personalizados**: Lógica de validación especializada
- **Transformadores de datos**: Conversión de formatos específicos

## Consideraciones de Rendimiento

### Optimizaciones Implementadas

- **Procesamiento por lotes**: Manejo eficiente de grandes volúmenes
- **Conexiones persistentes**: Reutilización de sesiones cuando es posible
- **Lazy loading**: Carga de datos bajo demanda
- **Memoria eficiente**: Liberación automática de recursos

### Escalabilidad

El diseño permite escalabilidad mediante:

- **Procesamiento paralelo**: Múltiples instancias de procesos
- **Distribución de carga**: Separación de archivos por lotes
- **Configuración adaptativa**: Ajuste automático según recursos

## Seguridad

### Gestión de Credenciales

- **No persistencia**: Las credenciales no se almacenan en disco
- **Entrada segura**: Interface gráfica para captura
- **Sesiones independientes**: Una sesión por proceso

### Validación de Datos

- **Sanitización**: Limpieza de datos de entrada
- **Validación de tipos**: Verificación de formatos esperados
- **Escape de caracteres**: Prevención de inyección de código

## Mantenimiento y Evolución

### Versionado del Core

El módulo core sigue versionado semántico:

- **Major**: Cambios incompatibles en interfaces
- **Minor**: Nuevas funcionalidades compatibles
- **Patch**: Correcciones de errores

### Actualización de Procesos

Los procesos específicos pueden evolucionar independientemente del core:

- **Compatibilidad hacia atrás**: El core mantiene interfaces estables
- **Migración gradual**: Actualización por partes del sistema
- **Testing independiente**: Validación aislada de cada proceso

Este diseño garantiza un sistema robusto, mantenible y escalable para la automatización de procesos web complejos.
