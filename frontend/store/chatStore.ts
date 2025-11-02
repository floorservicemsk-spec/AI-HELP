import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Message {
  id: string
  text: string
  isUser: boolean
  sources?: string[]
  timestamp: Date
}

interface ChatStore {
  messages: Message[]
  conversationId: string | null
  userId: string | null
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void
  setConversationId: (id: string) => void
  setUserId: (id: string) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set) => ({
      messages: [],
      conversationId: null,
      userId: null,
      addMessage: (message) =>
        set((state) => ({
          messages: [
            ...state.messages,
            {
              ...message,
              id: `msg_${Date.now()}_${Math.random()}`,
              timestamp: new Date(),
            },
          ],
        })),
      setConversationId: (id) => set({ conversationId: id }),
      setUserId: (id) => set({ userId: id }),
      clearMessages: () => set({ messages: [] }),
    }),
    {
      name: 'chat-storage',
    }
  )
)
