import React, { useState } from 'react';
import { Send, Mic } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, disabled = false }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <form onSubmit={handleSubmit} className="flex items-end space-x-3">
        <div className="flex-1 relative">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Escribe tu pregunta sobre normas de tránsito..."
            disabled={disabled}
            className="w-full resize-none rounded-2xl border border-gray-300 px-4 py-3 pr-12 focus:border-transit-500 focus:outline-none focus:ring-2 focus:ring-transit-200 disabled:bg-gray-50 disabled:text-gray-500 max-h-32 min-h-[48px]"
            rows={1}
            style={{
              height: 'auto',
              minHeight: '48px'
            }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement;
              target.style.height = 'auto';
              target.style.height = Math.min(target.scrollHeight, 128) + 'px';
            }}
          />
          
          {/* Voice Input Button (Placeholder) */}
          <button
            type="button"
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
            title="Entrada por voz (próximamente)"
          >
            <Mic className="w-5 h-5" />
          </button>
        </div>
        
        <button
          type="submit"
          disabled={!message.trim() || disabled}
          className="bg-transit-500 text-white rounded-full p-3 hover:bg-transit-600 focus:outline-none focus:ring-2 focus:ring-transit-200 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          title="Enviar mensaje"
        >
          <Send className="w-5 h-5" />
        </button>
      </form>
      
      <div className="mt-2 text-xs text-gray-500 text-center">
        Presiona Enter para enviar, Shift+Enter para nueva línea
      </div>
    </div>
  );
};

export default ChatInput;