// Configuración de la API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

// Interfaces para chat con RASA
export interface ChatRequest {
  sender_id: string;
  message: string;
  metadata?: Record<string, any>;
}

export interface BotMessageItem {
  text?: string;
  image?: string;
  buttons?: Array<{
    title: string;
    payload: string;
  }>;
  custom?: any;
}

export interface ChatResponse {
  sender_id: string;
  messages: BotMessageItem[];
  timestamp: string;
}

// Interfaces legacy (por si se necesitan)
export interface QueryRequest {
  query: string;
  max_results?: number;
  confidence_threshold?: number;
}

export interface QueryResponse {
  answer: string;
  confidence: number;
  sources: Array<{
    article: string;
    law: string;
    description: string;
    similarity_score: number;
    content_snippet: string;
  }>;
  processing_time: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  database_status: string;
}

class ApiService {
  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} - ${response.statusText}`);
    }

    return response.json();
  }

  // Genera o recupera sender_id de sessionStorage
  private getSenderId(): string {
    let senderId = sessionStorage.getItem('chat_sender_id');
    if (!senderId) {
      senderId = 'user_' + Math.random().toString(36).substring(2, 11) + Date.now();
      sessionStorage.setItem('chat_sender_id', senderId);
    }
    return senderId;
  }

  async queryTransitBot(query: string): Promise<ChatResponse> {
    const senderId = this.getSenderId();

    return this.makeRequest<ChatResponse>('/api/v1/chat/message', {
      method: 'POST',
      body: JSON.stringify({
        sender_id: senderId,
        message: query,
        metadata: {
          channel: 'web',
          timestamp: new Date().toISOString()
        }
      } as ChatRequest),
    });
  }

  async checkHealth(): Promise<HealthResponse> {
    return this.makeRequest<HealthResponse>('/api/v1/health');
  }


}

export const apiService = new ApiService();