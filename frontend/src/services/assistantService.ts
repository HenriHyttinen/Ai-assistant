/**
 * Assistant service for AI assistant API calls.
 */
import axios from 'axios';

// Use relative URLs to go through Vite proxy, or absolute URL if VITE_API_URL is set
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export type Message = {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  function_calls?: any[];
  function_results?: any[];
  token_count?: number;
  created_at: string;
};

export type Conversation = {
  id: string;
  user_id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  message_count?: number;
};

export type ChatRequest = {
  message: string;
  conversation_id?: string;
};

export type ChatResponse = {
  message: Message;
  user_message?: Message;  // User message that was sent
  conversation_id: string;
  function_calls?: any[];
  token_usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
};

class AssistantService {
  private async getAuthHeaders(): Promise<HeadersInit> {
    try {
      const { supabase } = await import('../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      if (session?.access_token) {
        headers['Authorization'] = `Bearer ${session.access_token}`;
      }
      return headers;
    } catch (error) {
      console.error('Error getting auth headers:', error);
    return {
      'Content-Type': 'application/json',
    };
    }
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      const headers = await this.getAuthHeaders();
      const response = await axios.post<ChatResponse>(
        `${API_BASE_URL}/api/assistant/chat`,
        request,
        { headers }
      );
      return response.data;
    } catch (error: any) {
      console.error('Error sending message:', error);
      throw new Error(error.response?.data?.detail || 'Failed to send message');
    }
  }

  async getConversations(): Promise<Conversation[]> {
    try {
      const headers = await this.getAuthHeaders();
      const response = await axios.get<Conversation[]>(
        `${API_BASE_URL}/api/assistant/conversations`,
        { headers }
      );
      return response.data;
    } catch (error: any) {
      console.error('Error getting conversations:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get conversations');
    }
  }

  async getConversationMessages(conversationId: string): Promise<Message[]> {
    try {
      const headers = await this.getAuthHeaders();
      const response = await axios.get<Message[]>(
        `${API_BASE_URL}/api/assistant/conversations/${conversationId}/messages`,
        { headers }
      );
      return response.data;
    } catch (error: any) {
      console.error('Error getting messages:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get messages');
    }
  }

  async deleteConversation(conversationId: string): Promise<void> {
    try {
      const headers = await this.getAuthHeaders();
      await axios.delete(
        `${API_BASE_URL}/api/assistant/conversations/${conversationId}`,
        { headers }
      );
    } catch (error: any) {
      console.error('Error deleting conversation:', error);
      throw new Error(error.response?.data?.detail || 'Failed to delete conversation');
    }
  }
}

export const assistantService = new AssistantService();

