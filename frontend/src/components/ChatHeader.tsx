import React from 'react';
import { Car, MessageCircle, Shield } from 'lucide-react';

const ChatHeader: React.FC = () => {
  return (
    <div className="bg-gradient-to-r from-transit-600 to-transit-700 text-white p-4 shadow-lg">
      <div className="flex items-center space-x-3">
        <div className="relative">
          <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
            <Car className="w-6 h-6" />
          </div>
          <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white animate-pulse-gentle"></div>
        </div>
        <div>
          <h1 className="text-lg font-bold">TránsitoBot Soacha</h1>
          <p className="text-sm text-white/80">Asistente de Normas de Tránsito</p>
        </div>
      </div>
    </div>
  );
};

export default ChatHeader;