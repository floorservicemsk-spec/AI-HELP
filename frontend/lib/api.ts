import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ChatRequest {
  question: string
  user_id?: string
  conversation_id?: string
}

export interface ChatResponse {
  answer: string
  context_sources: string[]
  conversation_id: string
}

export interface StatsResponse {
  total_chats: number
  total_sources: number
  total_chunks: number
  qdrant_points: number
  data_sources: Array<{
    id: number
    name: string
    type: string
    chunks_count: number
    created_at: string
  }>
}

export const api = {
  chat: {
    async sendMessage(request: ChatRequest): Promise<ChatResponse> {
      const response = await axios.post<ChatResponse>(
        `${API_URL}/api/chat`,
        request
      )
      return response.data
    },
  },
  auth: {
    async login(username: string, password: string): Promise<{ access_token: string }> {
      const response = await axios.post<{ access_token: string }>(
        `${API_URL}/api/auth/login`,
        { username, password }
      )
      return response.data
    },
  },
  admin: {
    async ingestXML(url?: string, token: string): Promise<any> {
      const response = await axios.post(
        `${API_URL}/api/admin/ingest/xml`,
        { url },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )
      return response.data
    },
    async ingestFile(file: File, token: string): Promise<any> {
      const formData = new FormData()
      formData.append('file', file)
      const response = await axios.post(
        `${API_URL}/api/admin/ingest/file`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      )
      return response.data
    },
    async getStats(token: string): Promise<StatsResponse> {
      const response = await axios.get<StatsResponse>(
        `${API_URL}/api/admin/stats`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )
      return response.data
    },
    async reindex(token: string): Promise<any> {
      const response = await axios.post(
        `${API_URL}/api/admin/reindex`,
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )
      return response.data
    },
  },
}
