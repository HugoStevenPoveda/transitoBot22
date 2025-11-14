import React from 'react';
import { Bot, User, ExternalLink } from 'lucide-react';
import { Message } from '../types/chat';

interface ChatMessageProps {
  message: Message;
  onButtonClick?: (payload: string) => void;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, onButtonClick }) => {
  const isBot = message.isBot;

  return (
    <div className={`flex ${isBot ? 'justify-start' : 'justify-end'} mb-4 animate-slide-up`}>
      <div className={`flex max-w-[80%] ${isBot ? 'flex-row' : 'flex-row-reverse'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isBot ? 'mr-3' : 'ml-3'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isBot 
              ? 'bg-gradient-to-br from-transit-500 to-transit-600 text-white' 
              : 'bg-gray-300 text-gray-600'
          }`}>
            {isBot ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
          </div>
        </div>

        {/* Message Content */}
        <div className={`rounded-2xl px-4 py-3 ${
          isBot 
            ? 'bg-white border border-gray-200 text-gray-800' 
            : 'bg-transit-500 text-white'
        }`}>
          {/* Texto del mensaje */}
          {message.text && (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {message.text}
            </p>
          )}

          {/* Imagen si viene */}
          {isBot && message.metadata?.image && (
            <div className="mt-2">
              <img
                src={message.metadata.image}
                alt="Imagen del bot"
                className="rounded-lg max-w-full"
              />
            </div>
          )}

          {/* Botones si vienen */}
          {isBot && message.metadata?.hasButtons && message.metadata.buttons && (
            <div className="mt-3 flex flex-wrap gap-2">
              {message.metadata.buttons.map((button, index) => (
                <button
                  key={index}
                  onClick={() => onButtonClick?.(button.payload)}
                  className="px-3 py-2 bg-transit-500 text-white text-sm rounded-lg hover:bg-transit-600 transition-colors"
                >
                  {button.title}
                </button>
              ))}
            </div>
          )}

          {/* Source Citation for Bot Messages */}
          {isBot && message.sources && message.sources.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-start space-x-2">
                  <ExternalLink className="w-4 h-4 text-gray-500 mt-0.5 flex-shrink-0" />
                  <div className="text-xs text-gray-600">
                    <p className="font-semibold text-gray-800 mb-1">Fuente Legal:</p>
                    <p><strong>{message.sources[0].article}</strong></p>
                    <p className="text-gray-500">{message.sources[0].law}</p>
                    {message.sources[0].description && (
                      <p className="mt-1 italic">{message.sources[0].description}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Timestamp */}
          <div className={`text-xs mt-2 ${
            isBot ? 'text-gray-400' : 'text-white/70'
          }`}>
            {message.timestamp.toLocaleTimeString('es-CO', {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;