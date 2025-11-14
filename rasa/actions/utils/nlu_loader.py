"""
Carga y parsea data/nlu.yml para extraer intenciones y sus ejemplos.
"""
import yaml
from pathlib import Path
from typing import Dict, List, Any


def load_nlu_data() -> Dict[str, Any]:
    """
    Carga el archivo data/nlu.yml y retorna el contenido parseado.

    Returns:
        Dict con el contenido del archivo NLU
    """
    nlu_path = Path(__file__).parent.parent.parent / "data" / "nlu.yml"

    try:
        with open(nlu_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data
    except FileNotFoundError:
        print(f"⚠️ Archivo NLU no encontrado en: {nlu_path}")
        return {"nlu": []}
    except Exception as e:
        print(f"❌ Error al cargar NLU: {e}")
        return {"nlu": []}


def get_all_intents() -> List[Dict[str, Any]]:
    """
    Obtiene todas las intenciones con sus ejemplos.

    Returns:
        Lista de diccionarios con {name, examples}
    """
    data = load_nlu_data()
    nlu_items = data.get("nlu", [])

    intents = []
    for item in nlu_items:
        if "intent" in item:
            intent_name = item["intent"]
            examples_text = item.get("examples", "")

            # Parsear ejemplos (vienen en formato multilinea con guiones)
            examples_list = []
            if examples_text:
                lines = examples_text.strip().split('\n')
                examples_list = [line.strip().lstrip('- ') for line in lines if line.strip().startswith('-')]

            intents.append({
                "name": intent_name,
                "examples": examples_list,
                "description": _generate_description(intent_name, examples_list)
            })

    return intents


def get_intent_by_name(intent_name: str) -> Dict[str, Any]:
    """
    Obtiene información de una intención específica.

    Args:
        intent_name: Nombre de la intención

    Returns:
        Dict con {name, examples, description} o None si no existe
    """
    all_intents = get_all_intents()
    for intent in all_intents:
        if intent["name"] == intent_name:
            return intent
    return None


def get_all_intents_by_category() -> Dict[str, List[Dict[str, Any]]]:
    """
    Obtiene todas las intenciones organizadas por categoría.

    Returns:
        Dict con categorías como keys y lista de intents como values
    """
    from .intent_categorizer import INTENT_CATEGORIES

    all_intents = get_all_intents()
    categorized = {}

    for categoria, intent_names in INTENT_CATEGORIES.items():
        categorized[categoria] = []
        for intent in all_intents:
            if intent["name"] in intent_names:
                categorized[categoria].append(intent)

    # Agregar intents no categorizados
    categorized_intent_names = [name for names in INTENT_CATEGORIES.values() for name in names]
    uncategorized = [intent for intent in all_intents if intent["name"] not in categorized_intent_names]

    if uncategorized:
        categorized["otros"] = uncategorized

    return categorized


def _generate_description(intent_name: str, examples: List[str]) -> str:
    """
    Genera una descripción básica a partir del nombre de la intención.

    Args:
        intent_name: Nombre de la intención
        examples: Lista de ejemplos

    Returns:
        Descripción generada
    """
    # Convertir snake_case a texto legible
    description = intent_name.replace('_', ' ').capitalize()

    # Agregar contexto si es posible
    if examples and len(examples) > 0:
        first_example = examples[0]
        if len(first_example) < 80:
            description += f" (ej: {first_example})"

    return description


# Cache para evitar recargar el archivo en cada llamada
_cached_intents = None

def get_all_intents_cached() -> List[Dict[str, Any]]:
    """
    Versión cacheada de get_all_intents para mejor performance.
    """
    global _cached_intents
    if _cached_intents is None:
        _cached_intents = get_all_intents()
    return _cached_intents
