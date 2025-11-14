import { Message } from '../types/chat';

export const mockResponses: Record<string, Omit<Message, 'id' | 'timestamp'>> = {
  'pico y placa': {
    text: `La multa por incumplir la restricción de pico y placa es de 15 salarios mínimos legales diarios vigentes (SMLDV).
     Aplica tambien en lo siguiente Invadir el carril exclusivo del SITP, Circular en vehículos o motocicletas por zonas no permitidas, 
     como andenes o ciclorrutas
es decir multiplicar el valor de un dia de trabajo de salario minimo X 15.

Además de la multa, el vehículo puede ser inmovilizado hasta por 24 horas.`,
    isBot: true,
    source: {
      article: 'Artículo 131 - Código Nacional de Tránsito Infracción C14',
      law: 'Ley 769 de 2002',
      description: 'Restricciones a la circulación de vehículos automotores'
    }
  },
  
  'estacionar': {
    text: `¿Qué significa? Dejar el vehículo estacionado en lugares no autorizados, como andenes, zonas verdes, 
            frente a garajes, en curvas o a menos de 5 metros de una esquina:

📄 **¿Cuál es la sanción? Multa de 15 SMLDV es decir multiplicar el valor de un dia de trabajo de salario minimo X 15.**
📋 **Si el conductor no está presente, el vehículo puede ser retirado con grúa.**


🛡️ (Contexto en Soacha: Es una de las principales causas del "círculo vicioso de congestión", 
    donde los conductores, por el trancón, estacionan mal, y a su vez, 
    empeoran el trancón para todos los demás.)`,
    isBot: true,
    source: {
      article: 'Artículo 131 Infracción C02 - Código Nacional de Tránsito',
      law: 'Ley 769 de 2002',
      description: 'Estacionar un Vehículo en Sitios Prohibidos'
    }
  },
  
  'velocidad': {
    text: `Los límites de velocidad en Colombia son:

🏙️ **Zona urbana:** 50 km/h máximo
🏘️ **Zona residencial:** 30 km/h máximo  
🏫 **Zona escolar:** 30 km/h máximo
🛣️ **Carreteras nacionales:** 80 km/h máximo
🚗 **Autopistas doble calzada sin pasos peatonales:** 120 km/h máximo

Exceder estos límites puede resultar en multas de 8 a 30 SMLDV y suspensión de la licencia.
Contexto en Soacha: A pesar de la congestión, hay tramos (especialmente en la Autopista Sur en horas de bajo tráfico) 
donde se cometen excesos que aumentan el riesgo de accidentes graves.`,
    isBot: true,
    source: {
      article: 'Artículo 106 Infracción C29 - Código Nacional de Tránsito',
      law: 'Ley 769 de 2002',
      description: 'Conducir a Velocidad Superior a la Máxima Permitida'
    }
  },
  
  'celular': {
    text: `❌ **NO puedes usar el celular mientras conduces.**

Está prohibido:
• Hablar por teléfono sin manos libres
• Enviar mensajes de texto
• Usar aplicaciones
• Sostener el dispositivo

✅ **Excepciones permitidas:**
• Uso con sistema manos libres
• GPS montado en soporte fijo
• Llamadas de emergencia

La multa por usar el celular mientras conduces es de 15 SMLDV (aproximadamente $522,500).`,
    isBot: true,
    source: {
      article: 'Artículo 131 numeral 24 - Código Nacional de Tránsito',
      law: 'Ley 769 de 2002, modificado por Ley 1383 de 2010',
      description: 'Prohibición del uso de dispositivos móviles durante la conducción'
    }
  },
  
  'semáforo amarillo': {
    text: `🟡 **Cuando el semáforo está en amarillo debes:**

✅ **Si puedes detenerte de forma segura:** DETENTE antes de la línea de pare.

⚠️ **Si ya estás muy cerca:** Continúa con precaución, pero NO aceleres.

❌ **Está prohibido:**
• Acelerar para "alcanzar" a pasar
• Frenar bruscamente si puedes continuar seguro

El amarillo es una señal de **precaución y preparación para detenerse**, no una invitación a acelerar.

Violar esta norma puede resultar en multa de 8 SMLDV.`,
    isBot: true,
    source: {
      article: 'Artículo 119 - Código Nacional de Tránsito',
      law: 'Ley 769 de 2002',
      description: 'Cumplimiento de las señales de tránsito'
    }
  },
  
  'zona azul': {
    text: `🅿️ **La zona azul es un sistema de parqueo regulado:**

⏰ **Tiempo límite:** Máximo 2 horas continuas
💰 **Costo:** Varía según la ciudad (aprox. $1,500-$3,000 por hora)
📱 **Pago:** A través de aplicaciones móviles o parquímetros

🚫 **Prohibiciones:**
• Parquear sin pagar
• Exceder el tiempo máximo
• Regresar inmediatamente después de las 2 horas

La multa por no pagar zona azul es de 8 SMLDV (aproximadamente $278,600).`,
    isBot: true,
    source: {
      article: 'Artículo 138 - Código Nacional de Tránsito',
      law: 'Ley 769 de 2002',
      description: 'Estacionamiento en zonas reguladas'
    }
  }
};

export function getResponse(userMessage: string): Omit<Message, 'id' | 'timestamp'> {
  const message = userMessage.toLowerCase();
  
  if (message.includes('pico') && message.includes('placa') || message.includes('sitio restringido')) {
    return mockResponses['pico y placa'];
  }
  
  if (message.includes('estacionar') || message.includes('sitio prohibido') || message.includes('Estacionar un vehiculo') || message.includes('Estacionar un Vehículo') || message.includes('sitio no permitido')) {
    return mockResponses['estacionar'];
  }
  
  if (message.includes('velocidad') || message.includes('límite') || message.includes('exceso de velocidad')) {
    return mockResponses['velocidad'];
  }
  
  if (message.includes('celular') || message.includes('teléfono') || message.includes('móvil')) {
    return mockResponses['celular'];
  }
  
  if (message.includes('amarillo') || message.includes('semáforo')) {
    return mockResponses['semáforo amarillo'];
  }
  
  if (message.includes('zona azul') || message.includes('parqueo') || message.includes('parqueadero')) {
    return mockResponses['zona azul'];
  }
  
  // Respuesta por defecto
  return {
    text: `Gracias por tu pregunta. Actualmente puedo ayudarte con información sobre:

• Transitar por Sitios Restringidos o en Horas Prohibidas Multa por pico y placa
• Estacionar un Vehículo en Sitios Prohibidos o no permitido  
• Límites de velocidad, exceso de velocidad

¿Sobre cuál de estos temas te gustaría saber más?`,
    isBot: true
  };
}