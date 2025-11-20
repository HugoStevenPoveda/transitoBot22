import logging
from typing import List, Dict, Any, Optional
from app.services.tools import AVAILABLE_TOOLS

logger = logging.getLogger(__name__)


class ToolManager:
    """
    Gestor de herramientas (tools) para function calling con LLMs.

    Responsable de:
    - Registrar y mantener las tools disponibles
    - Proporcionar definiciones de tools en formato Anthropic
    - Ejecutar tools con los parámetros proporcionados por el LLM
    """

    def __init__(self, db_repository=None, search_service=None):
        """
        Inicializa el ToolManager con las dependencias necesarias.

        Args:
            db_repository: Repositorio de base de datos (ChromaDB)
            search_service: Servicio de búsqueda híbrida
        """
        self.db_repository = db_repository
        self.search_service = search_service
        self._tool_instances = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """
        Inicializa las instancias de tools con sus dependencias.
        """
        try:
            # Inicializar HybridSearchTool si está disponible el search_service
            if self.search_service and "buscar_articulos_transito" in AVAILABLE_TOOLS:
                tool_class = AVAILABLE_TOOLS["buscar_articulos_transito"]
                self._tool_instances["buscar_articulos_transito"] = tool_class(
                    search_service=self.search_service
                )
                logger.info("✅ Tool 'buscar_articulos_transito' inicializado")

            # Inicializar EmailSenderTool
            if "enviar_email" in AVAILABLE_TOOLS:
                tool_class = AVAILABLE_TOOLS["enviar_email"]
                self._tool_instances["enviar_email"] = tool_class()
                logger.info("✅ Tool 'enviar_email' inicializado")

            # Aquí se pueden agregar más tools en el futuro

            logger.info(f"🔧 ToolManager inicializado con {len(self._tool_instances)} tool(s)")

        except Exception as e:
            logger.error(f"❌ Error inicializando tools: {e}")

    def get_available_tool_names(self) -> List[str]:
        """
        Retorna lista de nombres de tools disponibles.

        Returns:
            Lista de nombres de tools
        """
        return list(self._tool_instances.keys())

    def get_tool_definitions(self, tool_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Retorna definiciones de tools en formato Anthropic API.

        Args:
            tool_names: Lista de nombres de tools a incluir.
                       Si es None, retorna todas las tools disponibles.

        Returns:
            Lista de definiciones de tools en formato Anthropic
        """
        definitions = []

        try:
            # Determinar qué tools incluir
            if tool_names is None:
                # Incluir todas las tools disponibles
                tools_to_include = self._tool_instances.keys()
            else:
                # Incluir solo las tools especificadas que existan
                tools_to_include = [name for name in tool_names if name in self._tool_instances]

                # Advertir sobre tools no encontrados
                missing_tools = set(tool_names) - set(tools_to_include)
                if missing_tools:
                    logger.warning(f"⚠️ Tools no encontrados: {missing_tools}")

            # Obtener definiciones
            for tool_name in tools_to_include:
                tool_instance = self._tool_instances[tool_name]
                definition = tool_instance.get_definition()
                definitions.append(definition)
                logger.debug(f"📋 Definición agregada: {tool_name}")

            logger.info(f"📦 Retornando {len(definitions)} definición(es) de tool(s)")

        except Exception as e:
            logger.error(f"❌ Error obteniendo definiciones de tools: {e}")

        return definitions

    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta un tool con los parámetros proporcionados.

        Args:
            tool_name: Nombre del tool a ejecutar
            tool_input: Diccionario con los parámetros del tool

        Returns:
            Dict con el resultado de la ejecución

        Raises:
            ValueError: Si el tool no existe
        """
        try:
            # Validar que el tool exista
            if tool_name not in self._tool_instances:
                error_msg = f"Tool '{tool_name}' no existe. Tools disponibles: {list(self._tool_instances.keys())}"
                logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }

            # Obtener instancia del tool
            tool_instance = self._tool_instances[tool_name]

            logger.info(f"🔧 Ejecutando tool '{tool_name}' con input: {tool_input}")

            # Ejecutar tool
            result = tool_instance.execute(**tool_input)

            logger.info(f"✅ Tool '{tool_name}' ejecutado exitosamente")

            return result

        except Exception as e:
            logger.error(f"❌ Error ejecutando tool '{tool_name}': {e}")
            return {
                "success": False,
                "error": f"Error al ejecutar el tool: {str(e)}"
            }

    def is_tool_available(self, tool_name: str) -> bool:
        """
        Verifica si un tool está disponible.

        Args:
            tool_name: Nombre del tool

        Returns:
            True si el tool está disponible, False en caso contrario
        """
        return tool_name in self._tool_instances

    def get_tool_instance(self, tool_name: str):
        """
        Retorna la instancia de un tool específico.

        Args:
            tool_name: Nombre del tool

        Returns:
            Instancia del tool o None si no existe
        """
        return self._tool_instances.get(tool_name)
