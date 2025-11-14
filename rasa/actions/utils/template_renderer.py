"""
Motor de renderizado de templates Jinja2 para generar contextos dinámicos.
"""
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
from pathlib import Path
from typing import Dict, Any, Optional
import os


# Configurar el environment de Jinja2
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Crear environment con configuración personalizada
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,  # No escapar HTML ya que generamos texto plano
    trim_blocks=True,  # Eliminar primer newline después de bloque
    lstrip_blocks=True  # Eliminar espacios antes de bloques
)


def render_template(template_name: str, context: Dict[str, Any]) -> str:
    """
    Renderiza un template Jinja2 con el contexto dado.

    Args:
        template_name: Nombre del archivo de template (ej: 'base_cot.j2')
        context: Dict con variables para el template

    Returns:
        String con el template renderizado
    """
    try:
        template = jinja_env.get_template(template_name)
        rendered = template.render(**context)
        return rendered.strip()

    except TemplateNotFound:
        print(f"⚠️ Template no encontrado: {template_name}")
        print(f"   Buscando en: {TEMPLATES_DIR}")

        # Fallback a template base
        return _render_fallback_template(context)

    except Exception as e:
        print(f"❌ Error al renderizar template {template_name}: {e}")
        return _render_fallback_template(context)


def render_template_string(template_string: str, context: Dict[str, Any]) -> str:
    """
    Renderiza un template desde un string en lugar de archivo.

    Args:
        template_string: String con el contenido del template
        context: Dict con variables para el template

    Returns:
        String con el template renderizado
    """
    try:
        template = Template(template_string)
        return template.render(**context).strip()

    except Exception as e:
        print(f"❌ Error al renderizar template string: {e}")
        return ""


def get_context_for_intent(
    intent_name: str,
    confidence: float,
    tracking: str
) -> Dict[str, Any]:
    """
    Construye el contexto completo para renderizar template de una intención.

    Args:
        intent_name: Nombre de la intención
        confidence: Confianza de la clasificación (0-1)
        tracking: Historial de conversación
        responses: Respuestas asociadas a la intención
        stories: Historias relacionadas con la intención
        success_status: Estado de éxito detectado

    Returns:
        Dict con el contexto completo
    """
    return {
        "intent_name": intent_name,
        "confidence": round(confidence * 100, 2),
        "tracking_conversacion": tracking,
        "has_tracking": bool(tracking)
    }


def get_context_for_fallback(
    user_question: str,
    tracking: str,
    categorized_intents: Dict[str, list],
    intent_name: Optional[str] = None,
    confidence: float = 0.0
) -> Dict[str, Any]:
    """
    Construye el contexto completo para renderizar template de fallback.

    Args:
        user_question: Pregunta del usuario
        tracking: Historial de conversación
        categorized_intents: Intenciones organizadas por categoría
        all_stories: Todas las historias disponibles
        intent_name: Intención detectada (opcional)
        confidence: Confianza de la clasificación

    Returns:
        Dict con el contexto completo
    """
    return {
        "user_question": user_question,
        "tracking_conversacion": tracking,
        "categorized_intents": categorized_intents,
        "intent_name": intent_name or "desconocida",
        "confidence": round(confidence * 100, 2),
        # Información adicional
        "num_categories": len(categorized_intents),
        "has_tracking": bool(tracking)
    }


def _render_fallback_template(context: Dict[str, Any]) -> str:
    """
    Renderiza un template de fallback básico cuando no se encuentra el template.

    Args:
        context: Contexto de la conversación

    Returns:
        String con contexto básico
    """
    intent_name = context.get("intent_name", "desconocida")
    tracking = context.get("tracking_conversacion", "")

    fallback_text = f"""Eres un asistente especializado en el Código Nacional de Tránsito de Colombia.

**INTENCIÓN DETECTADA:** {intent_name}

**CONTEXTO DE LA CONVERSACIÓN:**
{tracking if tracking else "(Inicio de conversación)"}

**TU TAREA:**
Responde de forma clara, precisa y amigable a la pregunta del usuario.
Usa tu conocimiento sobre el código de tránsito de Colombia.
"""

    return fallback_text.strip()


def list_available_templates() -> list:
    """
    Lista todos los templates disponibles en el directorio.

    Returns:
        Lista de nombres de archivos de templates
    """
    if not TEMPLATES_DIR.exists():
        print(f"⚠️ Directorio de templates no existe: {TEMPLATES_DIR}")
        return []

    template_files = []
    for file_path in TEMPLATES_DIR.glob("*.j2"):
        template_files.append(file_path.name)

    return sorted(template_files)


def template_exists(template_name: str) -> bool:
    """
    Verifica si existe un template.

    Args:
        template_name: Nombre del template

    Returns:
        True si el template existe
    """
    template_path = TEMPLATES_DIR / template_name
    return template_path.exists()


def get_template_path(template_name: str) -> Path:
    """
    Obtiene la ruta completa de un template.

    Args:
        template_name: Nombre del template

    Returns:
        Path del template
    """
    return TEMPLATES_DIR / template_name


# Filtros personalizados de Jinja2
def format_list(items: list, separator: str = ", ") -> str:
    """
    Formatea una lista como string.
    """
    if not items:
        return ""
    return separator.join(str(item) for item in items)


def truncate_text(text: str, max_length: int = 150) -> str:
    """
    Trunca un texto a una longitud máxima.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + "..."


# Registrar filtros personalizados
jinja_env.filters['format_list'] = format_list
jinja_env.filters['truncate_text'] = truncate_text
