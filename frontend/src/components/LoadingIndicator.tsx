import React from 'react';
import { Search, Database, Zap } from 'lucide-react';

const LoadingIndicator: React.FC = () => {
  return (
    <div className="flex justify-start mb-4 animate-fade-in">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 bg-gradient-to-br from-transit-500 to-transit-600 rounded-full flex items-center justify-center">
          <Zap className="w-4 h-4 text-white animate-pulse" />
        </div>
        <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 max-w-xs">
          <div className="flex items-center space-x-2 mb-2">
            <Database className="w-4 h-4 text-transit-500 animate-pulse" />
            <span className="text-sm text-gray-600 font-medium">Procesando con IA...</span>
          </div>
          
          <div className="space-y-1">
            <div className="flex items-center space-x-2 text-xs text-gray-500">
              <div className="w-2 h-2 bg-transit-400 rounded-full animate-bounce"></div>
              <span>Vectorizando consulta</span>
            </div>
            <div className="flex items-center space-x-2 text-xs text-gray-500">
              <div className="w-2 h-2 bg-transit-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              <span>Buscando en ChromaDB</span>
            </div>
            <div className="flex items-center space-x-2 text-xs text-gray-500">
              <div className="w-2 h-2 bg-transit-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              <span>Generando respuesta</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingIndicator;