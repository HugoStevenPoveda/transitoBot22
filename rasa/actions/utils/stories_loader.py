"""
Carga y parsea data/openrouter/*.yml para extraer stories y rules.
"""
import yaml
from pathlib import Path
from typing import Dict, List, Any
import glob


def load_stories_data() -> List[Dict[str, Any]]:
    """
    Carga todos los archivos de stories en data/openrouter/*.yml

    Returns:
        Lista de stories parseadas
    """
    stories_path = Path(__file__).parent.parent.parent / "data" / "openrouter"
    all_stories = []

    try:
        # Buscar todos los archivos .yml en data/openrouter/
        pattern = str(stories_path / "*.yml")
        story_files = glob.glob(pattern)

        for file_path in story_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

                # Extraer stories
                if "stories" in data:
                    for story in data["stories"]:
                        all_stories.append({
                            "type": "story",
                            "name": story.get("story", ""),
                            "steps": story.get("steps", []),
                            "source_file": Path(file_path).name
                        })

                # Extraer rules
                if "rules" in data:
                    for rule in data["rules"]:
                        all_stories.append({
                            "type": "rule",
                            "name": rule.get("rule", ""),
                            "steps": rule.get("steps", []),
                            "source_file": Path(file_path).name
                        })

    except Exception as e:
        print(f"❌ Error al cargar stories: {e}")

    return all_stories


def get_all_stories() -> List[Dict[str, Any]]:
    """
    Obtiene todas las stories con información procesada.

    Returns:
        Lista de diccionarios con información de stories
    """
    raw_stories = load_stories_data()
    processed_stories = []

    for story in raw_stories:
        processed_story = {
            "type": story["type"],
            "name": story["name"],
            "steps": _extract_step_descriptions(story["steps"]),
            "intents": _extract_intents_from_steps(story["steps"]),
            "actions": _extract_actions_from_steps(story["steps"]),
            "flow_description": _generate_flow_description(story["steps"]),
            "source_file": story.get("source_file", "unknown")
        }
        processed_stories.append(processed_story)

    return processed_stories


def get_stories_for_intent(intent_name: str) -> List[Dict[str, Any]]:
    """
    Obtiene todas las stories que contienen una intención específica.

    Args:
        intent_name: Nombre de la intención

    Returns:
        Lista de stories que incluyen esa intención
    """
    all_stories = get_all_stories()
    matching_stories = []

    for story in all_stories:
        if intent_name in story["intents"]:
            matching_stories.append(story)

    return matching_stories


def get_related_intents_from_stories(intent_name: str) -> List[str]:
    """
    Obtiene intenciones relacionadas basándose en las stories.

    Args:
        intent_name: Nombre de la intención

    Returns:
        Lista de intenciones que aparecen en las mismas stories
    """
    stories_with_intent = get_stories_for_intent(intent_name)
    related_intents = set()

    for story in stories_with_intent:
        for intent in story["intents"]:
            if intent != intent_name:
                related_intents.add(intent)

    return list(related_intents)


def _extract_step_descriptions(steps: List[Dict[str, Any]]) -> List[str]:
    """
    Extrae descripciones legibles de los pasos de una story.

    Args:
        steps: Lista de pasos de la story

    Returns:
        Lista de descripciones de pasos
    """
    descriptions = []

    for step in steps:
        if "intent" in step:
            descriptions.append(f"Usuario: {step['intent']}")
        elif "action" in step:
            descriptions.append(f"Bot: {step['action']}")
        elif "slot_was_set" in step:
            descriptions.append(f"Slot set: {step['slot_was_set']}")
        else:
            descriptions.append(f"Step: {step}")

    return descriptions


def _extract_intents_from_steps(steps: List[Dict[str, Any]]) -> List[str]:
    """
    Extrae las intenciones de los pasos de una story.

    Args:
        steps: Lista de pasos

    Returns:
        Lista de nombres de intenciones
    """
    intents = []

    for step in steps:
        if "intent" in step:
            intents.append(step["intent"])

    return intents


def _extract_actions_from_steps(steps: List[Dict[str, Any]]) -> List[str]:
    """
    Extrae las acciones de los pasos de una story.

    Args:
        steps: Lista de pasos

    Returns:
        Lista de nombres de acciones
    """
    actions = []

    for step in steps:
        if "action" in step:
            actions.append(step["action"])

    return actions


def _generate_flow_description(steps: List[Dict[str, Any]]) -> str:
    """
    Genera una descripción textual del flujo de la story.

    Args:
        steps: Lista de pasos

    Returns:
        Descripción del flujo
    """
    step_descriptions = _extract_step_descriptions(steps)
    return " → ".join(step_descriptions)


def get_stories_by_type(story_type: str) -> List[Dict[str, Any]]:
    """
    Filtra stories por tipo (story o rule).

    Args:
        story_type: 'story' o 'rule'

    Returns:
        Lista de stories del tipo especificado
    """
    all_stories = get_all_stories()
    return [story for story in all_stories if story["type"] == story_type]


# Cache para evitar recargar archivos en cada llamada
_cached_stories = None


def get_all_stories_cached() -> List[Dict[str, Any]]:
    """
    Versión cacheada de get_all_stories para mejor performance.
    """
    global _cached_stories
    if _cached_stories is None:
        _cached_stories = get_all_stories()
    return _cached_stories


def clear_cache():
    """
    Limpia el cache de stories. Útil para testing o hot-reload.
    """
    global _cached_stories
    _cached_stories = None
