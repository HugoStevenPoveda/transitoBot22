import React from 'react';
import { MessageCircle, Car, FileText, Clock, Phone } from 'lucide-react';
import { SuggestionChip } from '../types/chat';

interface WelcomeScreenProps {
  onSuggestionClick: (question: string) => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onSuggestionClick }) => {
  const suggestions: SuggestionChip[] = [
    {
      id: '1',
      text: ' Transitar por sitios restringidos o horas prohibidas 💰 por pico y placa',
      question: '¿Cuál es la multa por pico y placa?'
    },
    {
      id: '2',
      text: '🚗  Estacionar un Vehículo en Sitios Prohibidos',
      question: '¿Que sucede si estaciono en sitio no permitido?'
    },
    {
      id: '3',
      text: '⚡ Conducir a Velocidad Superior a la Máxima Permitida',
      question: 'Límites de velocidad en la ciudad'
    }
    /*{
      id: '1',
      text: 'Transitar por sitios restringidos o horas prohibidas 💰 por pico y placa',
      question: '¿Cuál es la multa por pico y placa?'
    },
    {
      id: '2',
      text: '📄 Documentos obligatorios',
      question: '¿Qué papeles debo llevar en el carro?'
    },
    {
      id: '3',
      text: '🚗 Límites de velocidad',
      question: 'Límites de velocidad en la ciudad'
    },
    {
      id: '4',
      text: '📱 Uso del celular',
      question: '¿Puedo usar el celular mientras conduzco?'
    },
    {
      id: '5',
      text: '🚦 Semáforos en amarillo',
      question: '¿Qué hacer cuando el semáforo está en amarillo?'
    },
    {
      id: '6',
      text: '🅿️ Parqueo en zona azul',
      question: '¿Cómo funciona el parqueo en zona azul?'
    }*/
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 bg-gradient-to-br from-gray-50 to-white">
      <div className="max-w-md w-full text-center animate-fade-in">
        {/* Logo y Bienvenida */}
        <div className="mb-8">
          <div className="w-20 h-20 bg-gradient-to-br from-transit-500 to-transit-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
            <Car className="w-10 h-10 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            ¡Hola! Soy TránsitoBot Soacha 👋
          </h2>
          <p className="text-gray-600 leading-relaxed">
            Tu asistente virtual sobre normas de tránsito en Soacha tu apoyo cerca de ti. 
            Estoy aquí para ayudarte a resolver tus dudas de manera rápida y confiable.
          </p>
        </div>

        {/* Sugerencias */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
            Preguntas frecuentes
          </h3>
          <div className="grid grid-cols-1 gap-3">
            {suggestions.map((suggestion, index) => (
              <button
                key={suggestion.id}
                onClick={() => onSuggestionClick(suggestion.question)}
                className="group bg-white border border-gray-200 rounded-lg p-4 text-left hover:border-transit-300 hover:shadow-md transition-all duration-200 animate-slide-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-center space-x-3">
                  <span className="text-lg">{suggestion.text.split(' ')[0]}</span>
                  <span className="text-gray-700 group-hover:text-transit-600 transition-colors">
                    {suggestion.text.substring(suggestion.text.indexOf(' ') + 1)}
                  </span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Información adicional */}
        <div className="text-xs text-gray-500 bg-gray-50 rounded-lg p-3">
          <div className="flex items-center justify-center space-x-4">
            <div className="flex items-center space-x-1">
              <FileText className="w-3 h-3" />
              <span>Basado en normativa oficial</span>
            </div>
            <div className="flex items-center space-x-1">
              <Clock className="w-3 h-3" />
              <span>Respuestas instantáneas</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;