# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List, Optional
import requests
import re
import json
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# Importar utilidades
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# Importar módulos de utilidades
from utils import (
    intent_categorizer,
    responses_loader,
    stories_loader,
    template_renderer,
    success_tracker,
    nlu_loader
)


# URL base de la API de multas (cambiar por tu API real)
API_BASE_URL = "http://backrag:8000/api"
#API_BASE_URL = "http://localhost:8000/api"

# Umbral de confianza para considerar intención válida
CONFIDENCE_THRESHOLD = 0.5

# Intents que indican operaciones transaccionales
INTENTS_TRANSACCIONALES = [
    "consultar_multa",
    "pagar_multa",
    "validar_placa",
    "procesar_pago",
    "consultar_multa_especifica",
    "como_pagar_multa"
]

      
class ActionConsultarConOpenRouter(Action):
    """
    Consulta OpenRouter con contexto completo de la conversación.
    Envía: tracking, pregunta, intent y entidades al LLM.
    """

    def name(self) -> Text:
        return "action_consultar_con_openrouter"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 1. EXTRAER PREGUNTA DEL USUARIO
        pregunta = tracker.latest_message.get('text', '')

        # 2. EXTRAER INTENT
        intencion = tracker.latest_message.get('intent', {}).get('name', '')
        confidence = tracker.latest_message.get('intent', {}).get('confidence', 0)

        # 3. EXTRAER ENTIDADES
        entidades = tracker.latest_message.get('entities', [])

        # 4. EXTRAER TRACKING DE CONVERSACIÓN
        tracking_conversacion = self._extraer_tracking(tracker)

        # 5. NUEVO: DETERMINAR TEMPLATE SEGÚN CATEGORÍA
        template_name = intent_categorizer.get_template_for_intent(intencion)


        # 9. NUEVO: RENDERIZAR TEMPLATE DINÁMICO
        try:
            context_data = template_renderer.get_context_for_intent(
                intent_name=intencion,
                confidence=confidence,
                tracking=tracking_conversacion
            )

            context_system = template_renderer.render_template(template_name, context_data)

            print(f"[Template] Usando: {template_name}")
            print(f"\n{'='*80}")
            print(f"TEMPLATE RENDERIZADO ENVIADO AL LLM:")
            print(f"{'='*80}")
            print(context_system)
            print(f"{'='*80}\n")

        except Exception as e:
            print(f"⚠️ Error al renderizar template: {e}")
            # Fallback a contexto básico
            context_system = (
                "Eres un asistente experto en el Código Nacional de Tránsito de Colombia. "
                "Usa razonamiento interno (CoT) sin mostrarlo. "
                "Responde siempre de forma muy corta, concreta y basada solo en información real del tránsito. "
                "No inventes datos ni supongas información no dada. "
                "Cuando aplique, da opciones claras según el historial de consultas sobre fotomultas. "
                "Mantén coherencia con el contexto previo del usuario."
            )

        print(f"[tracking_conversacion] Context System:")
        print(f"//////////////"*50)
        print(f"{tracking_conversacion}")
        print(f"//////////////"*50)

        # 6. CONSTRUIR PAYLOAD
        payload = {
            "context": {
                "system": context_system,
                "user": tracking_conversacion
            },
            "pregunta": pregunta,
            "entidades": entidades,
            "intencion": intencion
        }

        print(f"[OpenRouter] Intent: {intencion}, Confidence: {confidence:.2f}")
        print(f"[OpenRouter] Pregunta: {pregunta[:100]}...")
        print(f"[OpenRouter] Entidades: {entidades}")

        # 7. LLAMAR AL ENDPOINT
        try:
            response = requests.post(
                f"{API_BASE_URL}/v1/anthropic",
                json=payload,
                timeout=30
            )
            print("RESPONSE: ", response.text)
            if response.status_code == 200:
                print("RESPONSERESPONSERESPONSERESPONSE: ",  response.json())
                data = response.json()
                print("ADDADADAADADAD: ",  data )
                answer = data.get("answer", "")
                model_used = data.get("model_used", "")
                processing_time = data.get("processing_time", 0)

                print(f"✅ OpenRouter respondió: {model_used} ({processing_time:.2f}s)")

                # 8. ENVIAR RESPUESTA AL USUARIO
                dispatcher.utter_message(text=answer)

            else:
                print(f"⚠️ OpenRouter error: HTTP {response.status_code}")
                dispatcher.utter_message(
                    text="Lo siento, no pude procesar tu consulta en este momento. ¿Podrías reformular tu pregunta?"
                )

        except requests.exceptions.RequestException as e:
            print(f"❌ Error llamando OpenRouter: {e}")
            dispatcher.utter_message(
                text="⚠️ El servicio de consulta avanzada no está disponible en este momento."
            )

        return []

    def _extraer_tracking(self, tracker: Tracker) -> str:
        """
        Extrae el historial de conversación del tracker de Rasa.
        Retorna un string con formato Usuario/Bot alternado.
        """
        mensajes = []

        # Obtener últimos 20 eventos para no sobrecargar el contexto
        eventos_recientes = tracker.events[-20:] if len(tracker.events) > 20 else tracker.events

        for event in eventos_recientes:
            event_type = event.get("event")

            # Capturar mensajes del usuario
            if event_type == "user":
                texto = event.get("text", "")
                if texto and texto.strip():
                    mensajes.append(f"Usuario: {texto}")

            # Capturar respuestas del bot
            elif event_type == "bot":
                texto = event.get("text", "")
                if texto and texto.strip():
                    mensajes.append(f"Bot: {texto}")

        # Si no hay historial, retornar string vacío
        if not mensajes:
            return ""

        return "\n".join(mensajes)


class ActionDefaultFallback(Action):
    """
    Acción de fallback que intenta con OpenRouter primero y luego BackRag.
    Se ejecuta cuando:
    - Intent es out_of_scope
    - Intent es consulta_codigo_transito
    - Intent tiene baja confianza (nlu_fallback)

    Flujo:
    1. Intenta responder con OpenRouter (usa contexto de conversación)
    2. Si OpenRouter falla → retorna vacío para activar BackRag
    """

    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Obtener el último intent y su confianza
        intent = tracker.latest_message.get('intent', {}).get('name')
        confidence = tracker.latest_message.get('intent', {}).get('confidence', 0)
        pregunta = tracker.latest_message.get('text', '')

        print(f"[Fallback] Intent: {intent}, Confidence: {confidence:.2f}")
        print(f"[Fallback] Intentando con OpenRouter con template fallback...")

        # OPCIÓN 1: INTENTAR CON OPENROUTER CON TEMPLATE FALLBACK
        try:
            # Extraer entidades
            entidades = tracker.latest_message.get('entities', [])

            # Extraer tracking de conversación
            tracking_conversacion = self._extraer_tracking(tracker)

            # NUEVO: Cargar todas las intenciones categorizadas
            categorized_intents = nlu_loader.get_all_intents_by_category()


            # NUEVO: Renderizar template fallback
            try:
                context_data = template_renderer.get_context_for_fallback(
                    user_question=pregunta,
                    tracking=tracking_conversacion,
                    categorized_intents=categorized_intents,
                    intent_name=intent,
                    confidence=confidence
                )

                context_system = template_renderer.render_template('fallback.j2', context_data)

                print(f"[Fallback Template] Categorías cargadas: {len(categorized_intents)}")
                print(f"\n{'='*80}")
                print(f"TEMPLATE FALLBACK RENDERIZADO ENVIADO AL LLM:")
                print(f"{'='*80}")
                print(context_system)
                print(f"{'='*80}\n")

            except Exception as e:
                print(f"⚠️ Error al renderizar template fallback: {e}")
                # Fallback a contexto básico
                context_system = (
                    "Eres un asistente experto en el Código Nacional de Tránsito de Colombia. "
                    "Usa razonamiento interno (CoT) sin mostrarlo. "
                    "Responde siempre de forma muy corta, concreta y basada solo en información real del tránsito. "
                    "No inventes datos ni supongas información no dada. "
                    "Cuando aplique, da opciones claras según el historial de consultas sobre fotomultas. "
                    "Mantén coherencia con el contexto previo del usuario."
                )

            # Construir payload
            payload = {
                "context": {
                    "system": context_system,
                    "user": tracking_conversacion
                },
                "pregunta": pregunta,
                "entidades": entidades,
                "intencion": intent or "fallback"
            }

            # Llamar a OpenRouter
            response = requests.post(
                f"{API_BASE_URL}/v1/anthropic",
                json=payload,
                timeout=15
            )
            print("RESPONSE ActionDefaultFallback: ", response.text)
            if response.status_code == 200:
                print("ActionDefaultFallbackActionDefaultFallbackActionDefaultFallbackActionDefaultFallback: ",  response.json())
                data = response.json()
                print("ADDADADAADADAD: ",  data )
                answer = data.get("answer", "")
                model_used = data.get("model_used", "")
                processing_time = data.get("processing_time", 0)

                print(f"✅ [Fallback→OpenRouter] Respondió: {model_used} ({processing_time:.2f}s)")

                # Enviar respuesta del LLM
                dispatcher.utter_message(text=answer)
                return []

            else:
                print(f"⚠️ [Fallback→OpenRouter] Error HTTP {response.status_code}, pasando a BackRag...")

        except requests.exceptions.RequestException as e:
            print(f"⚠️ [Fallback→OpenRouter] Error: {e}, pasando a BackRag...")
        except Exception as e:
            print(f"⚠️ [Fallback→OpenRouter] Error inesperado: {e}, pasando a BackRag...")

        # OPCIÓN 2: SI OPENROUTER FALLA → ACTIVAR BACKRAG
        print(f"[Fallback] OpenRouter no disponible, activando BackRag...")

        # Enviar mensaje vacío con metadata para que RouterBack active BackRag
        dispatcher.utter_message(
            text="",
            json_message={
                "custom": {
                    "fallback": True,
                    "intent": intent,
                    "confidence": confidence,
                    "reason": "openrouter_failed_then_backrag"
                }
            }
        )

        return []

    def _extraer_tracking(self, tracker: Tracker) -> str:
        """
        Extrae el historial de conversación del tracker de Rasa.
        Retorna un string con formato Usuario/Bot alternado.
        """
        mensajes = []

        # Obtener últimos 20 eventos para no sobrecargar el contexto
        eventos_recientes = tracker.events[-20:] if len(tracker.events) > 20 else tracker.events

        for event in eventos_recientes:
            event_type = event.get("event")

            # Capturar mensajes del usuario
            if event_type == "user":
                texto = event.get("text", "")
                if texto and texto.strip():
                    mensajes.append(f"Usuario: {texto}")

            # Capturar respuestas del bot
            elif event_type == "bot":
                texto = event.get("text", "")
                if texto and texto.strip():
                    mensajes.append(f"Bot: {texto}")

        # Si no hay historial, retornar string vacío
        if not mensajes:
            return ""

        return "\n".join(mensajes)


class ActionProcesarInfraccion(Action):
    """
    Procesa la descripción de la infracción del usuario.
    Extrae la entidad tipo_infraccion y dispara la pregunta sobre qué acción tomar.
    """

    def name(self) -> Text:
        return "action_procesar_infraccion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extraer entidad tipo_infraccion
        entidades = tracker.latest_message.get('entities', [])
        tipo_infraccion = None

        for entidad in entidades:
            if entidad.get('entity') == 'tipo_infraccion':
                tipo_infraccion = entidad.get('value')
                break

        # Si no se detectó la entidad, usar el texto completo
        if not tipo_infraccion:
            tipo_infraccion = tracker.latest_message.get('text', 'la infracción')

        print(f"[Procesar Infracción] Tipo detectado: {tipo_infraccion}")

        # Disparar la pregunta sobre qué acción tomar
        dispatcher.utter_message(response="utter_preguntar_accion")

        # Retornar el slot actualizado
        return [SlotSet("tipo_infraccion", tipo_infraccion)]


class ActionProcesarEleccion(Action):
    """
    Procesa la elección del usuario (pagar, curso o impugnar).
    Guarda la acción elegida y pregunta si desea recibir info por correo.
    """

    def name(self) -> Text:
        return "action_procesar_eleccion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Obtener el intent del usuario
        intent = tracker.latest_message.get('intent', {}).get('name')

        # Mapear intent a acción elegida
        accion_map = {
            'elegir_pagar': 'pagar',
            'elegir_curso': 'curso',
            'elegir_impugnar': 'impugnar'
        }

        accion_elegida = accion_map.get(intent, 'pagar')

        print(f"[Procesar Elección] Intent: {intent}, Acción: {accion_elegida}")

        # Disparar pregunta sobre envío de correo
        dispatcher.utter_message(response="utter_preguntar_envio_correo")

        # Retornar el slot actualizado
        return [SlotSet("accion_elegida", accion_elegida)]


class ActionEnviarInformacion(Action):
    """
    Procesa la respuesta sobre envío de correo.
    Usa el LLM con tools (buscar_articulos_transito y enviar_email) para:
    1. Buscar el artículo específico del código de tránsito violado
    2. Enviar correo con información detallada según la acción elegida
    """

    def name(self) -> Text:
        return "action_enviar_informacion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Obtener intent (afirmar o negar)
        intent = tracker.latest_message.get('intent', {}).get('name')
        enviar_correo = (intent == 'afirmar')

        # Si el usuario dijo NO
        if not enviar_correo:
            dispatcher.utter_message(response="utter_no_enviar_correo")
            return [SlotSet("enviar_correo", False)]

        # PASO 1: Obtener slots necesarios
        accion_elegida = tracker.get_slot('accion_elegida')
        tipo_infraccion = tracker.get_slot('tipo_infraccion')

        # PASO 2: Validar y extraer tipo_infraccion
        if not tipo_infraccion:
            # Intentar extraer de entidades
            entidades = tracker.latest_message.get('entities', [])
            for entidad in entidades:
                if entidad.get('entity') == 'tipo_infraccion':
                    tipo_infraccion = entidad.get('value')
                    break

        # Si aún no hay tipo_infraccion, usar valor genérico
        if not tipo_infraccion:
            tipo_infraccion = "infracción de tránsito (tipo no especificado)"
            print("⚠️ [ActionEnviarInformacion] No se encontró tipo_infraccion, usando valor genérico")

        print(f"[ActionEnviarInformacion] Acción elegida: {accion_elegida}")
        print(f"[ActionEnviarInformacion] Tipo infracción: {tipo_infraccion}")
        print(f"[ActionEnviarInformacion] Enviar correo: {enviar_correo}")

        # PASO 3: Extraer tracking de conversación
        tracking_conversacion = self._extraer_tracking(tracker)

        # Enriquecer el tracking con información de la infracción
        contexto_adicional = f"""
Usuario: [Infracción reportada: {tipo_infraccion}]
Usuario: [Eligió acción: {accion_elegida}]
Usuario: [Confirmó que SÍ quiere recibir información por correo]
"""
        tracking_conversacion += contexto_adicional

        # PASO 4: Extraer entidades
        entidades = tracker.latest_message.get('entities', [])

        # PASO 5: Construir prompt del sistema según la acción elegida
        context_system = self._construir_prompt_segun_accion(accion_elegida, tipo_infraccion)

        # PASO 6: Construir payload completo
        payload = {
            "context": {
                "system": context_system,
                "user": tracking_conversacion
            },
            "pregunta": f"El usuario quiere información sobre {accion_elegida} para su infracción: {tipo_infraccion}. Busca el artículo violado y envía toda la información detallada por correo.",
            "entidades": entidades,
            "intencion": "enviar_informacion_por_correo",
            "use_tools": True,
            "available_tools": ["enviar_email", "buscar_articulos_transito"]
        }

        print(f"[ActionEnviarInformacion] Tools disponibles: {payload['available_tools']}")
        print(f"[ActionEnviarInformacion] Pregunta construida: {payload['pregunta']}")
        print(f"[ActionEnviarInformacion] Context system (preview): {context_system[:200]}...")

        # PASO 7: Llamar al endpoint
        try:
            response = requests.post(
                f"{API_BASE_URL}/v1/anthropic",
                json=payload,
                timeout=30
            )

            print(f"[ActionEnviarInformacion] Response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")
                model_used = data.get("model_used", "")
                processing_time = data.get("processing_time", 0)

                print(f"✅ [ActionEnviarInformacion] LLM ejecutó tools y respondió en {processing_time:.2f}s")
                print(f"[ActionEnviarInformacion] Model usado: {model_used}")

                # Enviar respuesta al usuario
                dispatcher.utter_message(text=answer)

            else:
                print(f"⚠️ [ActionEnviarInformacion] Error HTTP {response.status_code}")
                dispatcher.utter_message(
                    text="Lo siento, no pude procesar el envío de información. Por favor, intenta de nuevo más tarde."
                )

        except requests.exceptions.RequestException as e:
            print(f"❌ [ActionEnviarInformacion] Error de red: {e}")
            dispatcher.utter_message(
                text="⚠️ El servicio de envío de información no está disponible en este momento. Por favor, intenta más tarde."
            )
        except Exception as e:
            print(f"❌ [ActionEnviarInformacion] Error inesperado: {e}")
            dispatcher.utter_message(
                text="Lo siento, ocurrió un error inesperado. Por favor, intenta de nuevo."
            )

        return [SlotSet("enviar_correo", True)]

    def _extraer_tracking(self, tracker: Tracker) -> str:
        """
        Extrae el historial de conversación del tracker de Rasa.
        Retorna un string con formato Usuario/Bot alternado.
        """
        mensajes = []

        # Obtener últimos 20 eventos para no sobrecargar el contexto
        eventos_recientes = tracker.events[-20:] if len(tracker.events) > 20 else tracker.events

        for event in eventos_recientes:
            event_type = event.get("event")

            # Capturar mensajes del usuario
            if event_type == "user":
                texto = event.get("text", "")
                if texto and texto.strip():
                    mensajes.append(f"Usuario: {texto}")

            # Capturar respuestas del bot
            elif event_type == "bot":
                texto = event.get("text", "")
                if texto and texto.strip():
                    mensajes.append(f"Bot: {texto}")

        # Si no hay historial, retornar string vacío
        if not mensajes:
            return ""

        return "\n".join(mensajes)

    def _construir_prompt_segun_accion(self, accion_elegida: str, tipo_infraccion: str) -> str:
        """
        Construye el prompt del sistema según la acción elegida por el usuario.
        Incluye instrucciones detalladas para usar las tools.
        """

        # Instrucciones comunes para todas las acciones
        instrucciones_tools = f"""
INSTRUCCIONES PARA USO DE HERRAMIENTAS:

1. **PRIMERO** usa la herramienta `buscar_articulos_transito` para:
   - Buscar el artículo específico del Código Nacional de Tránsito que se violó
   - Usar el tipo de infracción: "{tipo_infraccion}"
   - Obtener: número de artículo, descripción legal, sanciones y multas

2. **SEGUNDO** usa la herramienta `enviar_email` para:
   - Enviar al correo del usuario la información completa
   - INCLUIR OBLIGATORIAMENTE en el correo:
     * El artículo específico violado (del paso 1)
     * La descripción legal de la infracción
     * Las sanciones establecidas
     * La información sobre {accion_elegida} (según el tipo de acción)
"""

        # Prompts específicos según la acción elegida
        if accion_elegida == 'pagar':
            return f"""
Eres un asistente especializado en el Código Nacional de Tránsito de Colombia.

CONTEXTO:
- El usuario ha decidido PAGAR su infracción de tránsito
- Tipo de infracción: {tipo_infraccion}

{instrucciones_tools}

3. Estructura del correo para PAGAR:
   📋 Asunto: "Información para pago de tu infracción de tránsito"

   📌 INFRACCIÓN IDENTIFICADA
   - Artículo violado: [Resultado de buscar_articulos_transito]
   - Descripción legal: [Descripción completa]
   - Multa establecida: [Monto en SMLDV y pesos colombianos]

   💳 INFORMACIÓN DE PAGO
   - Pasos detallados para pagar
   - Plataformas oficiales de pago disponibles
   - Descuentos por pronto pago (si aplican)
   - Enlaces a portales de pago oficiales

   📅 PLAZOS IMPORTANTES
   - Fecha límite para descuento del 50%
   - Consecuencias de no pagar a tiempo

TONO: FORMAL, CLARO, ORIENTADO A LA ACCIÓN
"""

        elif accion_elegida == 'curso':
            return f"""
Eres un asistente especializado en el Código Nacional de Tránsito de Colombia.

CONTEXTO:
- El usuario ha decidido tomar un CURSO PEDAGÓGICO como alternativa
- Tipo de infracción: {tipo_infraccion}

{instrucciones_tools}

3. Estructura del correo para CURSO PEDAGÓGICO:
   📋 Asunto: "Información sobre curso pedagógico para tu infracción"

   📌 INFRACCIÓN IDENTIFICADA
   - Artículo violado: [Resultado de buscar_articulos_transito]
   - Descripción legal: [Descripción completa]

   📚 INFORMACIÓN DEL CURSO PEDAGÓGICO
   - Instituciones autorizadas para tomar el curso
   - Duración del curso (horas)
   - Costos aproximados
   - Requisitos de inscripción
   - Procedimiento para validar el curso ante autoridades
   - Beneficios (descuento en multa, puntos en licencia)

   ⚠️ CONDICIONES Y REQUISITOS
   - Verificar si esta infracción permite curso pedagógico
   - Plazos para tomar el curso
   - Documentos a presentar

TONO: INFORMATIVO, EDUCATIVO, MOTIVADOR
"""

        elif accion_elegida == 'impugnar':
            return f"""
Eres un asistente especializado en el Código Nacional de Tránsito de Colombia.

CONTEXTO:
- El usuario ha decidido IMPUGNAR su infracción de tránsito
- Tipo de infracción: {tipo_infraccion}

{instrucciones_tools}

3. Estructura del correo para IMPUGNACIÓN:
   📋 Asunto: "Información para impugnar tu infracción de tránsito"

   📌 INFRACCIÓN IDENTIFICADA
   - Artículo violado: [Resultado de buscar_articulos_transito]
   - Descripción legal completa
   - Elementos constitutivos que deben probarse

   ⚖️ PROCESO DE IMPUGNACIÓN
   - Documentos necesarios para impugnar
   - Entidades ante las cuales presentar el recurso
   - Plazos legales (términos de ley)
   - Formularios requeridos
   - Pasos detallados del proceso legal

   📌 CAUSALES COMUNES DE IMPUGNACIÓN
   - Error en identificación del vehículo o conductor
   - Falla en notificación legal
   - Prescripción de la infracción
   - Vicios de procedimiento
   - Argumentos de defensa técnica

   ⏰ PLAZOS CRÍTICOS
   - Días hábiles para presentar recurso
   - Consecuencias de perder los términos legales

TONO: SERIO, LEGAL, DETALLADO, TÉCNICO
"""

        else:
            # Fallback genérico
            return f"""
Eres un asistente especializado en el Código Nacional de Tránsito de Colombia.

CONTEXTO:
- El usuario ha solicitado información sobre su infracción de tránsito
- Tipo de infracción: {tipo_infraccion}

{instrucciones_tools}

3. Estructura del correo:
   📋 Asunto: "Información sobre tu infracción de tránsito"

   📌 INFRACCIÓN IDENTIFICADA
   - Artículo violado: [Resultado de buscar_articulos_transito]
   - Descripción legal
   - Sanciones establecidas

   📋 INFORMACIÓN GENERAL
   - Opciones disponibles (pagar, curso, impugnar)
   - Plazos importantes
   - Próximos pasos recomendados

TONO: INFORMATIVO, PROFESIONAL, CLARO
"""
