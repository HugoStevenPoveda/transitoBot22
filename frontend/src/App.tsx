import React, { useState, useRef, useEffect } from 'react';
import ChatHeader from './components/ChatHeader';
import WelcomeScreen from './components/WelcomeScreen';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import LoadingIndicator from './components/LoadingIndicator';
import { Message } from './types/chat';
import { apiService } from './services/api';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [showWelcome, setShowWelcome] = useState(true);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const generateId = () => Math.random().toString(36).substr(2, 9);

  const addMessage = (text: string, isBot: boolean, sources?: any[], metadata?: any) => {
    const newMessage: Message = {
      id: generateId(),
      text,
      isBot,
      timestamp: new Date(),
      sources,
      metadata
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleSendMessage = async (text: string) => {
    // Hide welcome screen
    setShowWelcome(false);

    // Add user message
    addMessage(text, false);

    // Show typing indicator
    setIsTyping(true);

    try {
      // Llamar al backend que consume RASA
      const response = await apiService.queryTransitBot(text);

      // RASA puede devolver múltiples mensajes
      if (response.messages && response.messages.length > 0) {
        response.messages.forEach((msg) => {
          // Extraer texto del mensaje
          const messageText = msg.text || '';

          // Si hay custom data con sources (del RAG), usarlas
          const sources = msg.custom?.sources;

          // Agregar el mensaje del bot
          addMessage(
            messageText,
            true,
            sources,
            {
              hasButtons: msg.buttons && msg.buttons.length > 0,
              buttons: msg.buttons,
              image: msg.image,
              custom: msg.custom
            }
          );
        });
      } else {
        // Fallback si no hay mensajes
        addMessage(
          'No recibí respuesta del servidor.',
          true
        );
      }
    } catch (error) {
      console.error('Error querying bot:', error);
      addMessage(
        'Lo siento, hubo un error al procesar tu consulta. Verifica que el servidor esté ejecutándose en http://localhost:8000',
        true
      );
    } finally {
      setIsTyping(false);
    }
  };

  const handleSuggestionClick = (question: string) => {
    handleSendMessage(question);
  };

  const handleButtonClick = (payload: string) => {
    // Cuando se hace click en un botón, enviar el payload como mensaje
    handleSendMessage(payload);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <ChatHeader />

      <div className="flex-1 flex flex-col overflow-hidden">
        {showWelcome ? (
          <WelcomeScreen onSuggestionClick={handleSuggestionClick} />
        ) : (
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                onButtonClick={handleButtonClick}
              />
            ))}

            {isTyping && <LoadingIndicator />}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <ChatInput onSendMessage={handleSendMessage} disabled={isTyping} />
    </div>
  );
}

export default App;