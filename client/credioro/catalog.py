"""Static catalog of the 42 CrediOro mini-processes."""

from __future__ import annotations

from typing import Any


def _p(
    code: str,
    description: str,
    group_name: str,
    owner: str,
    sort_order: int,
    is_automatable: int,
    is_critical: int,
) -> dict[str, Any]:
    return {
        "code": code,
        "description": description,
        "group_name": group_name,
        "owner": owner,
        "sort_order": sort_order,
        "is_automatable": is_automatable,
        "is_critical": is_critical,
    }


CATALOG_42: list[dict[str, Any]] = [
    _p("OSC", "SIMULACION DE CREDITO", "Simulator", "teller", 1, 1, 0),
    _p("CSB", "CONSULTA CLIENTE SBI", "Customer", "teller", 2, 1, 1),
    _p("OCC", "CONSULTA DEL CLIENTE", "Customer", "teller", 3, 1, 1),
    _p("PCL", "CONSULTA LISTAS DE CUMPLIMIENTO", "Customer", "teller", 4, 1, 1),
    _p("PAL", "AUTORIZACION LISTAS DE CUMPLIMIENTO", "Customer", "other", 5, 0, 1),
    _p("PNL", "NEGADO POR LISTAS", "Customer", "other", 6, 0, 0),
    _p("IVE", "INICIALIZACION VARIABLES MENSAJES ERROR", "Customer", "teller", 7, 1, 0),
    _p("LME", "MENSAJE DE PROCESO", "Customer", "teller", 8, 1, 0),
    _p("OCG", "CARGA DE FOTOS", "Customer", "teller", 9, 0, 0),
    _p("OFG", "AUTORIZACION TIPO DE ORO", "Customer", "teller", 10, 0, 1),
    _p("OAV", "CLIENTE APRUEBA VALOR", "Customer", "teller", 11, 0, 1),
    _p("PLB", "VALIDACION BIOMETRICA", "Customer", "teller", 12, 1, 0),
    _p("PAE", "AUTENTICACION EVIDENTE", "Customer", "teller", 13, 1, 0),
    _p("PCE", "FIN DEL PROCESO DE AUTENTICACION", "Customer", "teller", 14, 1, 0),
    _p("PEL", "ENROLAMIENTO Y BIOMETRIA CLIENTE", "Customer", "teller", 15, 1, 0),
    _p("OCD", "CONSULTA EN CENTRALES DE RIESGO", "Credit", "teller", 16, 1, 1),
    _p("OIF", "CAPTURA INFORMACION FINANCIERA", "Credit", "teller", 17, 1, 1),
    _p("OAC", "ANALISIS CENTRAL DE CREDITOS", "Credit", "teller", 18, 1, 1),
    _p("ORL", "REFERENCIACION FUENTE DE INGRESOS", "Credit", "teller", 19, 0, 0),
    _p("OUC", "APROBACION UNIDAD DE CREDITO", "Credit", "other", 20, 0, 1),
    _p("ORC", "RESULTADO DEL CREDITO", "Credit", "teller", 21, 1, 1),
    _p("OVB", "VINCULACION BASICA DE CLIENTES", "Credit", "teller", 22, 1, 1),
    _p("OVA", "VINCULACION AUTORIZADO", "Credit", "teller", 23, 1, 0),
    _p("CL2", "CONSULTA EN LISTAS DE CUMPLIMIENTO", "Onboarding", "teller", 24, 1, 1),
    _p("AL2", "AUTORIZACION POR LISTAS DE CUMPLIMIENTO", "Onboarding", "other", 25, 0, 1),
    _p("CLB", "VALIDACION BIOMETRICA", "Onboarding", "teller", 26, 1, 0),
    _p("AEV", "AUTENTICACION EVIDENTE", "Onboarding", "teller", 27, 1, 0),
    _p("EBI", "ENROLAMIENTO Y BIOMETRIA CLIENTE", "Onboarding", "teller", 28, 1, 0),
    _p("ORG", "REGISTRO DE GARANTIAS", "Onboarding", "teller", 29, 1, 1),
    _p("PVP", "VALIDACION CLIENTES PEP", "Onboarding", "teller", 30, 1, 0),
    _p("PAP", "AUTORIZA CLIENTES PEP", "Onboarding", "other", 31, 0, 0),
    _p("PID", "IMPRESION DE DOCUMENTOS", "Onboarding", "teller", 32, 1, 0),
    _p("PD1", "ENVIO WS CREACION GIRADOR DECEVAL", "Onboarding", "teller", 33, 1, 1),
    _p("PD2", "ENVIO WS CREACION PAGARE DECEVAL", "Onboarding", "teller", 34, 1, 1),
    _p("PD3", "ENVIO WS FIRMA PAGARE DECEVAL", "Onboarding", "teller", 35, 1, 1),
    _p("PAS", "ACTUALIZACION SBI", "Interface", "teller", 36, 1, 0),
    _p("PAC", "CREACION SBI", "Interface", "teller", 37, 1, 0),
    _p("INT", "INTERFACE (Integracion Inicial)", "Interface", "gyg", 38, 1, 0),
    _p("ORS", "REVISION GARANTIAS SENIOR", "Interface", "gyg", 39, 0, 0),
    _p("IN2", "INTERFACE (Integracion Final)", "Interface", "gyg", 40, 1, 0),
    _p("FIN", "FIN DE SOLICITUDES", "Interface", "gyg", 41, 1, 0),
    _p("ANS", "ANULACION DE SOLICITUDES", "Interface", "gyg", 42, 0, 0),
]
