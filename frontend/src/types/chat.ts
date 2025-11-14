export interface Source {
  article: string;
  law: string;
  description: string;
  similarity_score: number;
  content_snippet: string;
}

export interface MessageButton {
  title: string;
  payload: string;
}

export interface MessageMetadata {
  confidence?: number;
  processingTime?: number;
  hasButtons?: boolean;
  buttons?: MessageButton[];
  image?: string;
  custom?: any;
}

export interface Message {
  id: string;
  text: string;
  isBot: boolean;
  timestamp: Date;
  sources?: Source[];
  metadata?: MessageMetadata;
}

export interface SuggestionChip {
  id: string;
  text: string;
  question: string;
}
