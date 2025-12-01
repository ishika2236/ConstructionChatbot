import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface AuthRequest {
  email: string;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  user_email?: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  sources?: Source[];
}

export interface Source {
  file_name: string;
  page_number?: number;
  content_snippet: string;
  score?: number;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  message: string;
  sources: Source[];
  conversation_id: string;
  is_structured_extraction: boolean;
  structured_data?: any[];
}

export interface IngestionStatus {
  total_documents: number;
  processed_documents: number;
  total_chunks: number;
  status: string;
}

export const authAPI = {
  login: async (email: string): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/api/auth/login', { email });
    return response.data;
  },
};

export const chatAPI = {
  sendMessage: async (message: string, conversationId?: string): Promise<ChatResponse> => {
    const response = await api.post<ChatResponse>('/api/chat', {
      message,
      conversation_id: conversationId,
    });
    return response.data;
  },
};

export const ingestAPI = {
  ingestDocuments: async (): Promise<IngestionStatus> => {
    const response = await api.post<IngestionStatus>('/api/ingest');
    return response.data;
  },
  
  getStatus: async () => {
    const response = await api.get('/api/status');
    return response.data;
  },
};

export default api;
