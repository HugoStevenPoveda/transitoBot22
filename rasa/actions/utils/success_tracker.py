"""
Define y detecta criterios de éxito en conversaciones.
Permite saber cuándo se completó un objetivo conversacional.
"""
from typing import Dict, List, Any, Optional
import re


# Definición de criterios de éxito para diferentes flujos conversacionales
SUCCESS_CRITERIA = {
    "flujo_consulta_multa": {
        "objetivo": "Usuario obtuvo información completa sobre una multa específica",
        "intents_requeridos": ["consultar_multa_especifica"],
        "señales_exito": [
            "Usuario preguntó sobre tipo de multa",
            "Se proporcionó información de valor y consecuencias",
            "Usuario confirmó entendimiento"
        ],
        "keywords_confirmacion": ["gracias", "entendido", "ok", "perfecto", "claro"]
    },
    "flujo_documentos": {
        "objetivo": "Usuario conoce documentos obligatorios para conducir",
        "intents_requeridos": ["documentos_obligatorios"],
        "señales_exito": [
            "Se listaron todos los documentos obligatorios",
            "Usuario preguntó follow-up sobre documentos específicos"
        ],
        "keywords_confirmacion": ["gracias", "entendí", "ok"]
    },
    "flujo_accidente": {
        "objetivo": "Usuario sabe qué hacer ante un accidente",
        "intents_requeridos": ["que_hacer_accidente"],
        "posibles_seguimientos": [
            "accidente_sin_heridos",
            "accidente_con_heridos",
            "llamar_autoridades"
        ],
        "señales_exito": [
            "Se explicó procedimiento paso a paso",
            "Usuario hizo preguntas de clarificación"
        ],
        "keywords_confirmacion": ["entendido", "gracias", "claro"]
    },
    "flujo_licencia": {
        "objetivo": "Usuario obtuvo información sobre licencias",
        "intents_requeridos": ["tipos_licencias", "requisitos_licencia"],
        "señales_exito": [
            "Se explicaron tipos o requisitos de licencia",
            "Usuario confirmó que obtuvo la información"
        ],
        "keywords_confirmacion": ["gracias", "ok", "entendido"]
    },
    "flujo_alcoholemia": {
        "objetivo": "Usuario conoce límites y consecuencias de alcoholemia",
        "intents_requeridos": ["limite_alcoholemia", "sancion_conducir_ebrio"],
        "señales_exito": [
            "Se explicaron límites legales",
            "Se explicaron consecuencias"
        ],
        "keywords_confirmacion": ["entendido", "gracias", "claro"]
    },
    "flujo_estacionamiento": {
        "objetivo": "Usuario sabe dónde puede y no puede parquear",
        "intents_requeridos": ["estacionamiento_prohibido", "donde_parquear"],
        "señales_exito": [
            "Se explicaron reglas de estacionamiento",
            "Usuario hizo preguntas específicas"
        ],
        "keywords_confirmacion": ["ok", "gracias", "entendido"]
    }
}


def detect_success_in_tracking(tracking_conversacion: str) -> Dict[str, Any]:
    """
    Analiza el tracking de conversación para detectar si se completó un objetivo.

    Args:
        tracking_conversacion: Historial de la conversación

    Returns:
        Dict con información de éxito detectado
    """
    if not tracking_conversacion:
        return {
            "success_detected": False,
            "flow": None,
            "confidence": 0.0
        }

    # Detectar intenciones mencionadas en el tracking
    detected_intents = _extract_intents_from_tracking(tracking_conversacion)

    # Detectar keywords de confirmación
    has_confirmation = _detect_confirmation_keywords(tracking_conversacion)

    # Evaluar cada flujo
    for flow_name, criteria in SUCCESS_CRITERIA.items():
        required_intents = criteria.get("intents_requeridos", [])

        # Verificar si se cumplieron los intents requeridos
        intents_matched = any(intent in detected_intents for intent in required_intents)

        if intents_matched and has_confirmation:
            return {
                "success_detected": True,
                "flow": flow_name,
                "objetivo": criteria["objetivo"],
                "confidence": 0.9,
                "señales": criteria["señales_exito"]
            }

    # No se detectó éxito claro
    return {
        "success_detected": False,
        "flow": None,
        "confidence": 0.0,
        "detected_intents": detected_intents
    }


def get_success_criteria_for_intent(intent_name: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene los criterios de éxito asociados a una intención.

    Args:
        intent_name: Nombre de la intención

    Returns:
        Dict con criterios de éxito o None si no hay criterios definidos
    """
    for flow_name, criteria in SUCCESS_CRITERIA.items():
        required_intents = criteria.get("intents_requeridos", [])
        if intent_name in required_intents:
            return {
                "flow": flow_name,
                "objetivo": criteria["objetivo"],
                "señales_exito": criteria["señales_exito"]
            }

    return None


def should_suggest_next_step(tracking_conversacion: str, current_intent: str) -> Dict[str, Any]:
    """
    Determina si se debe sugerir un siguiente paso en la conversación.

    Args:
        tracking_conversacion: Historial de conversación
        current_intent: Intención actual

    Returns:
        Dict con sugerencia de siguiente paso
    """
    # Buscar flujos que incluyan la intención actual
    for flow_name, criteria in SUCCESS_CRITERIA.items():
        required_intents = criteria.get("intents_requeridos", [])
        posibles_seguimientos = criteria.get("posibles_seguimientos", [])

        if current_intent in required_intents and posibles_seguimientos:
            return {
                "should_suggest": True,
                "flow": flow_name,
                "next_steps": posibles_seguimientos,
                "mensaje": f"También puedo ayudarte con: {', '.join(posibles_seguimientos)}"
            }

    return {
        "should_suggest": False,
        "next_steps": []
    }


def _extract_intents_from_tracking(tracking: str) -> List[str]:
    """
    Extrae nombres de intenciones del tracking de conversación.

    Args:
        tracking: Texto del tracking

    Returns:
        Lista de intenciones detectadas
    """
    # Buscar patrones de intenciones comunes en el tracking
    # Por ahora, una implementación simple
    detected = []

    # Lista de intenciones conocidas para buscar
    from .intent_categorizer import INTENT_CATEGORIES

    all_intent_names = [intent for intents in INTENT_CATEGORIES.values() for intent in intents]

    for intent in all_intent_names:
        # Convertir intent_name a palabras clave
        keywords = intent.split('_')
        if any(keyword in tracking.lower() for keyword in keywords):
            detected.append(intent)

    return detected


def _detect_confirmation_keywords(tracking: str) -> bool:
    """
    Detecta si hay palabras clave de confirmación en el tracking.

    Args:
        tracking: Texto del tracking

    Returns:
        True si hay confirmación detectada
    """
    confirmation_keywords = [
        "gracias", "ok", "entendido", "perfecto", "claro",
        "vale", "de acuerdo", "comprendo", "entiendo",
        "muy bien", "excelente", "genial"
    ]

    tracking_lower = tracking.lower()

    return any(keyword in tracking_lower for keyword in confirmation_keywords)


def get_flow_description(flow_name: str) -> str:
    """
    Obtiene la descripción de un flujo conversacional.

    Args:
        flow_name: Nombre del flujo

    Returns:
        Descripción del objetivo del flujo
    """
    if flow_name in SUCCESS_CRITERIA:
        return SUCCESS_CRITERIA[flow_name]["objetivo"]

    return "Flujo conversacional"


def get_all_flows() -> List[str]:
    """
    Obtiene la lista de todos los flujos definidos.

    Returns:
        Lista de nombres de flujos
    """
    return list(SUCCESS_CRITERIA.keys())
