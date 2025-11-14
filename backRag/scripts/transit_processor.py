import docx
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ArticuloTransito:
    """Estructura para almacenar información de un artículo del código de tránsito."""
    numero: str
    titulo: str
    contenido: str
    capitulo: Optional[str] = None
    seccion: Optional[str] = None
    metadata: Optional[Dict] = None

class ProcesadorCodigoTransito:
    """Procesador avanzado para el código de tránsito colombiano."""
    
    def __init__(self):
        self.articulos: List[ArticuloTransito] = []
        
    def procesar_codigo_transito(self, nombre_archivo: str) -> List[ArticuloTransito]:
        """
        Extrae y procesa artículos del código de tránsito con metadatos enriquecidos.
        
        Args:
            nombre_archivo (str): Ruta al archivo .docx del código de tránsito
            
        Returns:
            List[ArticuloTransito]: Lista de artículos procesados con metadatos
        """
        try:
            doc = docx.Document(nombre_archivo)
            logger.info(f"Archivo '{nombre_archivo}' cargado exitosamente")
        except FileNotFoundError:
            logger.error(f"Error: El archivo '{nombre_archivo}' no fue encontrado.")
            return []
        except Exception as e:
            logger.error(f"Error al cargar el archivo: {e}")
            return []

        # Extraer texto completo preservando estructura
        texto_completo = []
        for parrafo in doc.paragraphs:
            if parrafo.text.strip():  # Solo agregar párrafos no vacíos
                texto_completo.append(parrafo.text.strip())

        texto_unido = "\n".join(texto_completo)
        
        # Procesar artículos con regex más robusto
        articulos_raw = self._segmentar_por_articulos(texto_unido)
        
        # Procesar cada artículo y extraer metadatos
        articulos_procesados = []
        capitulo_actual = None
        seccion_actual = None
        
        for i, chunk in enumerate(articulos_raw):
            if not chunk.strip():
                continue
                
            # Detectar capítulos y secciones
            capitulo_actual = self._detectar_capitulo(chunk) or capitulo_actual
            seccion_actual = self._detectar_seccion(chunk) or seccion_actual
            
            # Procesar artículo individual
            articulo = self._procesar_articulo_individual(
                chunk, capitulo_actual, seccion_actual, i
            )
            
            if articulo:
                articulos_procesados.append(articulo)
        
        self.articulos = articulos_procesados
        logger.info(f"Procesados {len(articulos_procesados)} artículos exitosamente")
        
        return articulos_procesados
    
    def _segmentar_por_articulos(self, texto: str) -> List[str]:
        """Segmenta el texto por artículos usando regex mejorado."""
        # Patrones más robustos para detectar artículos
        patrones = [
            r'Artículo\s+(\d+[°º]?\.?)',  # Artículo 123° o Artículo 123.
            r'ARTÍCULO\s+(\d+[°º]?\.?)',  # ARTÍCULO 123°
            r'Art\.\s+(\d+[°º]?\.?)',     # Art. 123°
        ]
        
        # Usar el patrón más común encontrado
        for patron in patrones:
            matches = re.findall(patron, texto, re.IGNORECASE)
            if len(matches) > 10:  # Si encuentra muchos matches, usar este patrón
                chunks = re.split(patron, texto, flags=re.IGNORECASE)
                return self._limpiar_chunks(chunks, patron)
        
        # Fallback al método original si regex falla
        return texto.split("Artículo ")
    
    def _limpiar_chunks(self, chunks: List[str], patron: str) -> List[str]:
        """Limpia y reconstruye los chunks después del split."""
        chunks_limpios = []
        for i in range(1, len(chunks), 2):  # Los números están en índices impares
            if i + 1 < len(chunks):
                numero = chunks[i]
                contenido = chunks[i + 1]
                chunk_completo = f"Artículo {numero} {contenido}".strip()
                if len(chunk_completo) > 50:  # Filtrar chunks muy cortos
                    chunks_limpios.append(chunk_completo)
        
        return chunks_limpios
    
    def _detectar_capitulo(self, texto: str) -> Optional[str]:
        """Detecta si el texto contiene información de capítulo."""
        patrones_capitulo = [
            r'CAPÍTULO\s+([IVX]+|[0-9]+)\.?\s*([^\n]+)',
            r'Capítulo\s+([IVX]+|[0-9]+)\.?\s*([^\n]+)',
        ]
        
        for patron in patrones_capitulo:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return f"Capítulo {match.group(1)}: {match.group(2).strip()}"
        
        return None
    
    def _detectar_seccion(self, texto: str) -> Optional[str]:
        """Detecta si el texto contiene información de sección."""
        patrones_seccion = [
            r'SECCIÓN\s+([IVX]+|[0-9]+)\.?\s*([^\n]+)',
            r'Sección\s+([IVX]+|[0-9]+)\.?\s*([^\n]+)',
        ]
        
        for patron in patrones_seccion:
            match = re.search(patron, texto, re.IGNORECASE)
            if match:
                return f"Sección {match.group(1)}: {match.group(2).strip()}"
        
        return None
    
    def _procesar_articulo_individual(
        self, 
        chunk: str, 
        capitulo: Optional[str], 
        seccion: Optional[str],
        indice: int
    ) -> Optional[ArticuloTransito]:
        """Procesa un artículo individual y extrae sus metadatos."""
        
        # Extraer número del artículo
        match_numero = re.search(r'Artículo\s+(\d+[°º]?)', chunk, re.IGNORECASE)
        if not match_numero:
            return None
        
        numero = match_numero.group(1)
        
        # Extraer título (primera línea después del número)
        lineas = chunk.split('\n')
        titulo = ""
        contenido_inicio = 1
        
        for i, linea in enumerate(lineas[1:], 1):
            if linea.strip() and not linea.strip().startswith('Artículo'):
                # Si la línea parece ser un título (corta, sin punto final)
                if len(linea.strip()) < 100 and not linea.strip().endswith('.'):
                    titulo = linea.strip()
                    contenido_inicio = i + 1
                break
        
        # Extraer contenido principal
        contenido_lineas = lineas[contenido_inicio:]
        contenido = '\n'.join(contenido_lineas).strip()
        
        # Crear metadatos adicionales
        metadata = {
            'longitud_caracteres': len(contenido),
            'longitud_palabras': len(contenido.split()),
            'indice_documento': indice,
            'contiene_multa': 'multa' in contenido.lower() or 'sanción' in contenido.lower(),
            'contiene_prohibicion': 'prohib' in contenido.lower() or 'no podrá' in contenido.lower(),
            'es_definicion': 'definición' in contenido.lower() or 'se entiende por' in contenido.lower(),
        }
        
        return ArticuloTransito(
            numero=numero,
            titulo=titulo,
            contenido=contenido,
            capitulo=capitulo,
            seccion=seccion,
            metadata=metadata
        )
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del procesamiento."""
        if not self.articulos:
            return {}
        
        total_articulos = len(self.articulos)
        articulos_con_multa = sum(1 for a in self.articulos if a.metadata.get('contiene_multa', False))
        articulos_con_prohibicion = sum(1 for a in self.articulos if a.metadata.get('contiene_prohibicion', False))
        
        longitudes = [a.metadata.get('longitud_caracteres', 0) for a in self.articulos]
        
        return {
            'total_articulos': total_articulos,
            'articulos_con_multa': articulos_con_multa,
            'articulos_con_prohibicion': articulos_con_prohibicion,
            'longitud_promedio': sum(longitudes) / len(longitudes) if longitudes else 0,
            'longitud_minima': min(longitudes) if longitudes else 0,
            'longitud_maxima': max(longitudes) if longitudes else 0,
        }
    
    def exportar_para_vectorizacion(self) -> List[Dict]:
        """Exporta los artículos en formato optimizado para vectorización."""
        documentos = []
        
        for articulo in self.articulos:
            # Crear texto optimizado para embeddings
            texto_para_embedding = f"Artículo {articulo.numero}"
            if articulo.titulo:
                texto_para_embedding += f": {articulo.titulo}"
            texto_para_embedding += f"\n\n{articulo.contenido}"
            
            documento = {
                'id': f"articulo_{articulo.numero}",
                'texto': texto_para_embedding,
                'metadata': {
                    'numero_articulo': articulo.numero,
                    'titulo': articulo.titulo,
                    'capitulo': articulo.capitulo,
                    'seccion': articulo.seccion,
                    'tipo_documento': 'codigo_transito',
                    'fuente': 'Código Nacional de Tránsito Terrestre - Ley 769 de 2002',
                    **articulo.metadata
                }
            }
            documentos.append(documento)
        
        return documentos

# Función de uso principal (compatible con tu código actual)
def procesar_codigo_transito(nombre_archivo: str) -> List[str]:
    """
    Función de compatibilidad que mantiene la interfaz original.
    """
    procesador = ProcesadorCodigoTransito()
    articulos = procesador.procesar_codigo_transito(nombre_archivo)
    
    # Convertir a formato original (solo texto)
    chunks_texto = []
    for articulo in articulos:
        texto_completo = f"Artículo {articulo.numero}"
        if articulo.titulo:
            texto_completo += f": {articulo.titulo}"
        texto_completo += f"\n\n{articulo.contenido}"
        chunks_texto.append(texto_completo)
    
    return chunks_texto

# Ejemplo de uso avanzado
if __name__ == "__main__":
    # Usar la versión mejorada
    procesador = ProcesadorCodigoTransito()
    articulos = procesador.procesar_codigo_transito("CodigoNacionaldeTransitoTerrestre.docx")
    
    # Mostrar estadísticas
    stats = procesador.obtener_estadisticas()
    print("=== ESTADÍSTICAS DEL PROCESAMIENTO ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # Mostrar algunos ejemplos
    if articulos:
        print(f"\n=== EJEMPLOS DE ARTÍCULOS PROCESADOS ===")
        for i, articulo in enumerate(articulos[:3]):
            print(f"\n--- Artículo {articulo.numero} ---")
            print(f"Título: {articulo.titulo}")
            print(f"Capítulo: {articulo.capitulo}")
            print(f"Contenido: {articulo.contenido[:300]}...")
            print(f"Metadatos: {articulo.metadata}")
    
    # Exportar para vectorización
    documentos_vectorizacion = procesador.exportar_para_vectorizacion()
    print(f"\n=== PREPARADO PARA VECTORIZACIÓN ===")
    print(f"Total documentos: {len(documentos_vectorizacion)}")
    print(f"Ejemplo de documento:")
    if documentos_vectorizacion:
        print(documentos_vectorizacion[0])