"""
Carga y parsea data/responses.yml para extraer respuestas asociadas a intenciones.
"""
import yaml
from pathlib import Path
from typing import Dict, List, Any


def load_responses_data() -> Dict[str, Any]:
    """
    Carga el archivo data/responses.yml y retorna el contenido parseado.

    Returns:
        Dict con el contenido del archivo responses
    """
    responses_path = Path(__file__).parent.parent.parent / "data" / "responses.yml"

    try:
        with open(responses_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data
    except FileNotFoundError:
        print(f"⚠️ Archivo responses no encontrado en: {responses_path}")
        return {"responses": {}}
    except Exception as e:
        print(f"❌ Error al cargar responses: {e}")
        return {"responses": {}}


def get_all_responses() -> Dict[str, Any]:
    """
    Obtiene todas las respuestas del archivo.

    Returns:
        Dict con todas las respuestas {utter_name: content}
    """
    data = load_responses_data()
    responses = data.get("responses", {})

    # Procesar cada response para extraer el texto
    processed_responses = {}
    for utter_name, utter_content in responses.items():
        if isinstance(utter_content, list) and len(utter_content) > 0:
            # Tomar el primer elemento de la lista
            first_response = utter_content[0]
            if isinstance(first_response, dict) and "text" in first_response:
                processed_responses[utter_name] = first_response["text"]
            else:
                processed_responses[utter_name] = str(first_response)
        else:
            processed_responses[utter_name] = str(utter_content)

    return processed_responses


def get_responses_for_intent(intent_name: str) -> Dict[str, str]:
    """
    Obtiene las respuestas asociadas a una intención específica.

    Busca respuestas que coincidan con el patrón: utter_{intent_name}
    También busca variaciones comunes.

    Args:
        intent_name: Nombre de la intención (ej: tipos_multa)

    Returns:
        Dict con {utter_name: response_text}
    """
    all_responses = get_all_responses()
    intent_responses = {}

    # Buscar respuestas exactas
    expected_utter_name = f"utter_{intent_name}"

    for utter_name, response_text in all_responses.items():
        # Coincidencia exacta
        if utter_name == expected_utter_name:
            intent_responses[utter_name] = response_text
        # Coincidencia parcial (para casos como multa_exceso_velocidad)
        elif intent_name in utter_name:
            intent_responses[utter_name] = response_text

    return intent_responses


def get_responses_by_category(category: str, intent_names: List[str]) -> Dict[str, str]:
    """
    Obtiene todas las respuestas para una categoría de intenciones.

    Args:
        category: Nombre de la categoría
        intent_names: Lista de nombres de intenciones en la categoría

    Returns:
        Dict con todas las respuestas de esa categoría
    """
    category_responses = {}

    for intent_name in intent_names:
        intent_responses = get_responses_for_intent(intent_name)
        category_responses.update(intent_responses)

    return category_responses


def get_response_preview(response_text: str, max_length: int = 150) -> str:
    """
    Genera un preview corto de una respuesta.

    Args:
        response_text: Texto completo de la respuesta
        max_length: Longitud máxima del preview

    Returns:
        Preview de la respuesta
    """
    if len(response_text) <= max_length:
        return response_text

    # Truncar y agregar ...
    return response_text[:max_length].rsplit(' ', 1)[0] + "..."


def search_responses_by_keyword(keyword: str) -> Dict[str, str]:
    """
    Busca respuestas que contengan una palabra clave.

    Args:
        keyword: Palabra clave a buscar

    Returns:
        Dict con respuestas que contienen la keyword
    """
    all_responses = get_all_responses()
    matching_responses = {}

    keyword_lower = keyword.lower()

    for utter_name, response_text in all_responses.items():
        if keyword_lower in response_text.lower() or keyword_lower in utter_name.lower():
            matching_responses[utter_name] = response_text

    return matching_responses


# Cache para evitar recargar el archivo en cada llamada
_cached_responses = None


def get_all_responses_cached() -> Dict[str, str]:
    """
    Versión cacheada de get_all_responses para mejor performance.
    """
    global _cached_responses
    if _cached_responses is None:
        _cached_responses = get_all_responses()
    return _cached_responses


def clear_cache():
    """
    Limpia el cache de responses. Útil para testing o hot-reload.
    """
    global _cached_responses
    _cached_responses = None
