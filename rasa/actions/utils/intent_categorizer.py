"""
Categoriza intenciones en grupos temáticos y mapea a templates.
"""
from typing import Dict, List

# Mapeo de intenciones a categorías temáticas
INTENT_CATEGORIES: Dict[str, List[str]] = {
  "fotomultas": [
    "preguntar_fotomulta",
    "plazo_fotomulta",
    "descuentos_fotomulta",
    "impugnar_fotomulta",
    "costos_fotomulta",
    "consultar_notificacion",
    "consultar_propietario_conductor",
    "consultar_suspension_licencia",
    "consultar_estado_fotomulta",
    "consultar_proceso_cobro",
    "consultar_curso_pedagogico",
    "consultar_validez_fotomulta",
    "consultar_tiempos_proceso",
    "consultar_prescripcion",
    "consultar_documentos_requeridos",
    "consultar_compra_venta",
    "consultar_inmovilizacion"
]
}


def get_category_for_intent(intent_name: str) -> str:
    """
    Obtiene la categoría a la que pertenece una intención.

    Args:
        intent_name: Nombre de la intención

    Returns:
        Nombre de la categoría o 'general' si no está categorizada
    """
    for categoria, intents in INTENT_CATEGORIES.items():
        if intent_name in intents:
            return categoria

    return "general"


def get_template_for_intent(intent_name: str) -> str:
    """
    Obtiene el nombre del template asociado a una intención.

    Args:
        intent_name: Nombre de la intención

    Returns:
        Nombre del archivo de template (ej: 'categoria_multas_sanciones.j2')
    """
    category = get_category_for_intent(intent_name)

    # Mapeo especial para intenciones conversacionales
    if category == "conversacional":
        if intent_name in ["out_of_scope", "consulta_codigo_transito"]:
            return "fallback.j2"
        else:
            return "base_cot.j2"

    # Para el resto, usar template de categoría
    return f"categoria_{category}.j2"


def get_intents_in_category(category: str) -> List[str]:
    """
    Obtiene todas las intenciones de una categoría específica.

    Args:
        category: Nombre de la categoría

    Returns:
        Lista de nombres de intenciones
    """
    return INTENT_CATEGORIES.get(category, [])


def get_all_categories() -> List[str]:
    """
    Obtiene la lista de todas las categorías disponibles.

    Returns:
        Lista de nombres de categorías
    """
    return list(INTENT_CATEGORIES.keys())


def get_category_display_name(category: str) -> str:
    """
    Obtiene un nombre legible para mostrar de una categoría.

    Args:
        category: Nombre de la categoría

    Returns:
        Nombre formateado para mostrar
    """
    display_names = {
        "multas_sanciones": "Multas y Sanciones",
        "licencias": "Licencias de Conducción",
        "alcoholemia": "Alcoholemia y Drogas",
        "documentos": "Documentos Obligatorios",
        "senales": "Señales de Tránsito",
        "velocidad": "Límites de Velocidad",
        "accidentes": "Accidentes de Tránsito",
        "motocicletas": "Motocicletas",
        "peatones": "Peatones",
        "estacionamiento": "Estacionamiento",
        "seguridad": "Cinturón y Seguridad",
        "celular": "Celular y Distracciones",
        "comparendos": "Comparendos y Procedimientos",
        "conversacional": "Conversación General"
    }

    return display_names.get(category, category.replace('_', ' ').title())


def get_intent_count_by_category() -> Dict[str, int]:
    """
    Cuenta cuántas intenciones hay en cada categoría.

    Returns:
        Dict con {categoria: cantidad}
    """
    counts = {}
    for categoria, intents in INTENT_CATEGORIES.items():
        counts[categoria] = len(intents)
    return counts
