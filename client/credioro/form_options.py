"""
config/form_options.py
----------------------
Opciones parametrizadas para los formularios y procesos del módulo
de Control de Garantías CrediOro (Banco Unión).
"""

# Tipos de Identificación de Cliente
TIPO_DOCUMENTO_OPTS: dict[str, str] = {
    "CC": "Cédula de Ciudadanía",
    "CE": "Cédula de Extranjería",
    "PA": "Pasaporte",
    "PPT": "Permiso por Protección Temporal",
}

# ── Simulador SIIF ─────────────────────────────────────────────────────────────

# Tipos de Identificación con values exactos del campo SIIF (N043)
# value="1" → CC | value="2" → CE | value="8" → PPT
TIPO_DOC_SIMULADOR_OPTS: dict[str, str] = {
    "1": "Cédula de Ciudadanía (CC)",
    "2": "Cédula de Extranjería (CE)",
    "8": "Permiso por Protección Temporal (PPT)",
}

# Tipos de Oro válidos para el select tipooro1 del SIIF
TIPO_ORO_SIMULADOR_OPTS: list[str] = [
    "ORO 18 KTS ITALIANO",
    "ORO 18 KTS NACIONAL",
    "ORO 16 KILATES",
    "ORO 14 KILATES",
    "ORO MONEDA",
]

# Sufijo numérico de los campos SIIF según tipo de oro (ORG)
TIPO_ORO_SUFFIX_MAP: dict[str, int] = {
    "ORO 18 KTS ITALIANO": 1,
    "ORO 18 KTS NACIONAL": 2,
    "ORO 16 KILATES": 3,
    "ORO 14 KILATES": 4,
    "ORO MONEDA": 5,
}

# Piezas de joyería soportadas en el registro de garantías (ORG)
PIEZAS_CANONICAS: list[str] = [
    "Anillos",
    "Aretes",
    "Cadenas",
    "Dijes",
    "Pulseras",
    "Relojes",
    "Monedas",
    "Tobilleras",
    "Brazaletes",
    "Accesorios",
]

# Opciones SI/NO para Reloj y Oro Blanco (select SIIF)
SI_NO_OPTS: dict[str, str] = {
    "SI": "Sí",
    "NO": "No",
}

PLAZO_INICIAL_SIIF = "06"

# ── Tejidos de Joyas y Nomenclatura para Descripción en SIIF ──────────────────
TEJIDOS_JOYAS_CATALOGO: dict[str, dict[str, str]] = {
    "BBDO": {
        "codigo": "BBDO",
        "nombre": "Tejido Barbado",
        "etiqueta": "BBDO — Tejido Barbado",
        "descripcion": "Eslabones aplanados y trenzados. Variedad de grosores en sus cadenas.",
    },
    "BBDI": {
        "codigo": "BBDI",
        "nombre": "Tejido Barbado Diamantado",
        "etiqueta": "BBDI — Tejido Barbado Diamantado",
        "descripcion": "Eslabones de tejido barbado con facetados en la superficie de cada eslabón (apariencia bicolor).",
    },
    "BBCO": {
        "codigo": "BBCO",
        "nombre": "Tejido Barbado Cuadrado",
        "etiqueta": "BBCO — Tejido Barbado Cuadrado",
        "descripcion": "Eslabones de tejido barbado con forma rectangular en cada eslabón.",
    },
    "FIGO": {
        "codigo": "FIGO",
        "nombre": "Tejido Fígaro (Cartier)",
        "etiqueta": "FIGO — Tejido Fígaro (Cartier)",
        "descripcion": "Eslabones aplanados y trenzados 3x1 (tres eslabones cortos y uno largo).",
    },
    "FGDO": {
        "codigo": "FGDO",
        "nombre": "Tejido Fígaro Diamantado",
        "etiqueta": "FGDO — Tejido Fígaro Diamantado",
        "descripcion": "Eslabones con facetados en la superficie de cada eslabón (apariencia de oro bicolor).",
    },
    "ALIA": {
        "codigo": "ALIA",
        "nombre": "Tejido Ancla Italiana",
        "etiqueta": "ALIA — Tejido Ancla Italiana",
        "descripcion": "Eslabones iguales que al trenzar forman una cadena estilo ancla marina o industrial.",
    },
    "SMLA": {
        "codigo": "SMLA",
        "nombre": "Tejido Semilla",
        "etiqueta": "SMLA — Tejido Semilla",
        "descripcion": "Eslabones en forma de semilla aplanados y trenzados.",
    },
    "CORN": {
        "codigo": "CORN",
        "nombre": "Tejido Cordón",
        "etiqueta": "CORN — Tejido Cordón",
        "descripcion": "Diseño en espiral retorcido que se asemeja a una cuerda o cordón.",
    },
    "GUCI": {
        "codigo": "GUCI",
        "nombre": "Tejido Gucci",
        "etiqueta": "GUCI — Tejido Gucci",
        "descripcion": "Eslabones ovalados huecos con dos orificios donde se unen.",
    },
    "GUPA": {
        "codigo": "GUPA",
        "nombre": "Tejido Gucci con Placa",
        "etiqueta": "GUPA — Tejido Gucci con Placa",
        "descripcion": "Eslabones ovalados huecos Gucci con placa central para grabado de nombres o símbolos.",
    },
    "CIVL": {
        "codigo": "CIVL",
        "nombre": "Tejido Chival",
        "etiqueta": "CIVL — Tejido Chival",
        "descripcion": "Eslabones aplanados y trenzados 3x1 con un eslabón de mayor volumen cada tres regulares.",
    },
    "BIZO": {
        "codigo": "BIZO",
        "nombre": "Tejido Bizantino",
        "etiqueta": "BIZO — Tejido Bizantino",
        "descripcion": "Entrelazado de anillos que crea un patrón en forma de diamante o V invertida.",
    },
    "MLTR": {
        "codigo": "MLTR",
        "nombre": "Tejido Militar (Bolas)",
        "etiqueta": "MLTR — Tejido Militar (Bolas)",
        "descripcion": "Pequeñas esferas de tamaño uniforme espaciadas de forma equidistante.",
    },
    "CBLE": {
        "codigo": "CBLE",
        "nombre": "Tejido Cable",
        "etiqueta": "CBLE — Tejido Cable",
        "descripcion": "Eslabones ovalados o redondos interconectados, uniformes en tamaño y forma.",
    },
    "VCNO": {
        "codigo": "VCNO",
        "nombre": "Tejido Veneciano (Caja)",
        "etiqueta": "VCNO — Tejido Veneciano (Caja)",
        "descripcion": "Eslabones cuadrados o con forma de caja a partir de alambre aplanado.",
    },
    "CDZO": {
        "codigo": "CDZO",
        "nombre": "Tejido Cola de Zorro",
        "etiqueta": "CDZO — Tejido Cola de Zorro",
        "descripcion": "Eslabones en forma de V entrelazados que crean una textura continua compacta.",
    },
    "CUBO": {
        "codigo": "CUBO",
        "nombre": "Tejido Cubana (Trigo)",
        "etiqueta": "CUBO — Tejido Cubana (Trigo)",
        "descripcion": "Diseño trenzado similar a espiga de trigo con eslabones en grupos de cuatro hilos.",
    },
    "CHNA": {
        "codigo": "CHNA",
        "nombre": "Tejido Chinesca",
        "etiqueta": "CHNA — Tejido Chinesca",
        "descripcion": "Diseño de malla intrincado y detallado que imita el tejido tradicional chino.",
    },
    "ESPO": {
        "codigo": "ESPO",
        "nombre": "Tejido Espina de Pescado",
        "etiqueta": "ESPO — Tejido Espina de Pescado",
        "descripcion": "Eslabones planos y delgados dispuestos en paralelo asemejando espinas de pez.",
    },
    "FRCO": {
        "codigo": "FRCO",
        "nombre": "Tejido Franco",
        "etiqueta": "FRCO — Tejido Franco",
        "descripcion": "Diseño de eslabones entrelazados continuos en forma de «V».",
    },
}

TEJIDOS_SELECT_OPTIONS: list[str] = [
    "— Personalizado / Ninguno —",
    *[f"{k} — {v['nombre']}" for k, v in TEJIDOS_JOYAS_CATALOGO.items()],
]


# Categorías para captura de fotografías de prendas
CATEGORIA_FOTO_OPTS: dict[str, str] = {
    "PiezaCompleta": "Vista General de la Pieza",
    "Contramarca": "Contramarca / Sello de Ley",
    "Balanza": "Prenda en Balanza (Peso visible)",
    "Documento": "Factura / Certificado de Origen",
}

# Atribuciones y Límites de Aprobación por Rol de Tasador
ROLES_TASADOR_OPTS: dict[str, dict] = {
    "Tasador Junior": {
        "limite_monto": 5_000_000,
        "descripcion": "Hasta $5,000,000 COP per operación",
    },
    "Tasador Senior": {
        "limite_monto": 20_000_000,
        "descripcion": "Hasta $20,000,000 COP per operación",
    },
    "Jefe de CrediOro": {
        "limite_monto": 50_000_000,
        "descripcion": "Hasta $50,000,000 COP per operación",
    },
    "Comité de Crédito": {
        "limite_monto": 999_999_999,
        "descripcion": "Sin Límite (Aprobación Especial)",
    },
}

# Estados de Custodia Física de la Prenda
ESTADO_CUSTODIA_OPTS: dict[str, str] = {
    "BovedaAgencia": "En Bóveda Agencia",
    "EnTransito": "En Tránsito (Transportadora de Valores)",
    "BovedaCentral": "En Bóveda Central de Valores",
    "EntregadoTitular": "Entregado a Titular",
    "EntregadoTercero": "Entregado a Tercero Autorizado",
    "Rematado": "Rematado por Incumplimiento",
}

# Ubicaciones Físicas de Custodia
UBICACIONES_CUSTODIA_OPTS: list[str] = [
    "Agencia Principal - Bóveda 1",
    "Agencia Norte - Bóveda A",
    "Agencia Sur - Bóveda B",
    "Bóveda Central de Valores (Sede Matriz)",
    "Transportadora de Valores (Prosegur / TVS)",
]

# Estados de Validación de Cliente
ESTADO_VALIDACION_CLIENTE: dict[str, str] = {
    "APROBADO": "Aprobado para Crédito",
    "BLOQUEADO_INSOLVENCIA": "Bloqueado por Insolventes",
    "BLOQUEADO_EMBARGO": "Bloqueado por Embargo / Medida Cautelar",
    "BLOQUEADO_INTERNO": "Bloqueado por Restricción Interna",
}


# ── OVB — Opciones de Vinculación ──────────────────────────────────────────────

# Municipios de Colombia con código DANE
# Clave: nombre visible en front | Valor: código DANE para inyección en SIIF
MUNICIPIOS_DANE: dict[str, str] = {
    "Bogotá D.C.": "11001",
    "Medellín": "05001",
    "Cali": "76001",
    "Barranquilla": "08001",
    "Bucaramanga": "68001",
    "Cartagena": "13001",
    "Cúcuta": "54001",
    "Pereira": "66001",
    "Manizales": "17001",
    "Ibagué": "73001",
    "Santa Marta": "47001",
    "Villavicencio": "50001",
    "Pasto": "52001",
    "Montería": "23001",
    "Valledupar": "20001",
    "Armenia": "63001",
    "Sincelejo": "70001",
    "Popayán": "19001",
    "Neiva": "41001",
    "Tunja": "15001",
    "Florencia": "18001",
    "Quibdó": "27001",
    "Riohacha": "44001",
    "San Andrés": "88001",
    "Mocoa": "86001",
    "Arauca": "81001",
    "Yopal": "85001",
    "Mitú": "97001",
    "Puerto Carreño": "99001",
    "Inírida": "94001",
    "San José del Guaviare": "95001",
    "Leticia": "91001",
    "Bello": "05088",
    "Soacha": "25754",
    "Buenaventura": "76109",
    "Soledad": "08758",
    "Itagüí": "05360",
    "Palmira": "76520",
    "Barrancabermeja": "68081",
    "Envigado": "05266",
    "Girardot": "25307",
    "Floridablanca": "68276",
    "Turbo": "05837",
    "Tulúa": "76834",
    "Duitama": "15238",
    "Sogamoso": "15759",
    "Girón": "68307",
    "Dosquebradas": "66170",
    "Maicao": "44430",
    "Apartadó": "05045",
    "Rionegro": "05615",
    "Zipaquirá": "25899",
    "Fusagasugá": "25290",
    "Facatativá": "25269",
    "Ciénaga": "47189",
    "Magangué": "13430",
    "Lorica": "23417",
    "Campoalegre": "41132",
    "Espinal": "73268",
    "Tumaco": "52835",
    "Ocaña": "54498",
    "Cartago": "76147",
    "La Virginia": "66400",
    "Chía": "25175",
    "Mosquera": "25473",
    "Madrid": "25430",
}

# Mapeo inverso de código DANE -> Nombre del Municipio
DANE_TO_MUNICIPIO: dict[str, str] = {v: k for k, v in MUNICIPIOS_DANE.items()}

# Tipo de Nacionalidad
# Clave: código SIIF | Valor: etiqueta visible en el front
TIPO_NACIONALIDAD_OPTS: dict[str, str] = {
    "1": "NACIONAL",
    "2": "EXTRANJERO",
}

# País (sólo Colombia por ahora)
# Clave: código SIIF | Valor: etiqueta visible en el front
PAIS_OPTS: dict[str, str] = {
    "CO": "Colombia",
}

# Género
# Clave: código SIIF | Valor: etiqueta visible en el front
GENERO_OPTS: dict[str, str] = {
    "1": "MASCULINO",
    "2": "FEMENINO",
    "3": "NO BINARIO",
    "4": "TRANS",
}

# Detalle de Actividad Económica (N0027)
# Clave: código SIIF | Valor: descripción visible en el front
DETALLE_ACTIVIDAD_OPTS: dict[str, str] = {
    "1": "AGROPECUARIO",
    "2": "MINERIA",
    "3": "INDUSTRIAL",
    "4": "CONSTRUCCION",
    "5": "COMERCIAL",
    "6": "TRANSPORTE",
    "7": "SERVICIOS",
}

# Cargo del empleado (N0028)
# Clave: código SIIF | Valor: descripción visible en el front
CARGO_OPTS: dict[str, str] = {
    "1":  "DIRECTIVO",
    "2":  "MANDO MEDIO",
    "3":  "SUBALTERNO",
    "4":  "AUXILIAR",
    "5":  "OPERARIO",
    "99": "NO APLICA",
}

# Sí / No para campos fiscales (DeclaraRenta N0044, Contabilidad N0045, DirReporte N0046)
# Clave: código SIIF | Valor: etiqueta visible en el front
SI_NO_SIIF_OPTS: dict[str, str] = {
    "1": "SÍ",
    "2": "NO",
}


# ── OVA — Opciones de Vinculación de Beneficiario / Autorizado ─────────────────
# Clave: código numérico inyectado en SIIF (N0003) | Valor: texto descriptivo en front
PARENTESCO_OPTS: dict[str, str] = {
    "1": "ABUELO(A)",
    "2": "CONYUGE",
    "3": "CUÑADO(A)",
    "4": "HERMANO(A)",
    "5": "HIJO(A)",
    "6": "OTRO-AMIGO U OTRO NO FAMILIA",
    "7": "PADRES",
    "8": "PRIMO(A)",
    "9": "SUEGRO(A)",
    "10": "TIO(A)",
}

# Mapeo inverso: Texto descriptivo -> Código numérico SIIF
# Mapeo inverso: Texto descriptivo -> Código numérico SIIF
TEXTO_TO_PARENTESCO_CODE: dict[str, str] = {v: k for k, v in PARENTESCO_OPTS.items()}


# ── OIF — Captura de Información Financiera ─────────────────────────────────────

TIPO_VIVIENDA_OPTS: dict[str, str] = {
    "1": "PROPIA",
    "2": "ALQUILADA MENOR A UN AÑO",
    "3": "ALQUILADA MAYOR A UN AÑO",
    "4": "FAMILIAR",
}

ESTADO_CIVIL_OPTS: dict[str, str] = {
    "1": "SOLTERO",
    "2": "CASADO",
    "3": "SEPARADO",
    "4": "DIVORCIADO",
    "5": "VIUDO",
    "6": "RELIGIOSO",
    "7": "UNION LIBRE",
}

PERSONAS_CARGO_OPTS: dict[str, str] = {
    "0": "0 PERSONAS",
    "1": "1 PERSONA",
    "2": "2 PERSONAS",
    "3": "3 PERSONAS",
    "4": "4 PERSONAS",
    "5": "MAS DE 4 PERSONAS",
}

ESTRATO_OPTS: dict[str, str] = {
    "1": "ESTRATO 1",
    "2": "ESTRATO 2",
    "3": "ESTRATO 3",
    "4": "ESTRATO 4",
    "5": "ESTRATO 5",
    "6": "ESTRATO 6",
}

NIVEL_ESTUDIOS_OPTS: dict[str, str] = {
    "1": "PRIMARIA",
    "2": "BACHILLERATO",
    "3": "TECNICO",
    "4": "TECNOLOGO",
    "5": "UNIVERSITARIO",
}

OCUPACION_OPTS: dict[str, str] = {
    "1": "EMPLEADO",
    "2": "INDEPENDIENTE",
    "3": "INDEPENDIENTE CON EMPRESA",
    "4": "TRANSPORTADOR",
    "5": "PENSIONADO",
    "6": "RENTISTA DE CAPITAL",
    "7": "AMA DE CASA",
    "8": "ESTUDIANTE",
    "9": "SIN OCUPACION CON INGRESOS",
}

TIPO_CONTRATO_OPTS: dict[str, str] = {
    "1": "FIJO",
    "2": "INDEFINIDO",
    "3": "TEMPORAL",
}

ANTIGUEDAD_OPTS: dict[str, str] = {
    "1": "MENOR A UN AÑO",
    "2": "ENTRE 1 AÑO Y 6 AÑOS",
    "3": "MAYOR A 6 AÑOS",
}
