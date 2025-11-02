'use client'

import { useState, useRef, useEffect } from 'react'
import Head from 'next/head'
import { Send, Loader2 } from 'lucide-react'
import { useChatStore, Message } from '../store/chatStore'
import { api } from '../lib/api'

export default function ChatPage() {
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { messages, conversationId, userId, addMessage, setConversationId, setUserId } = useChatStore()

  useEffect(() => {
    // Generate userId if not exists
    if (!userId) {
      const newUserId = `user_${Date.now()}`
      setUserId(newUserId)
    }
    if (!conversationId) {
      const newConvId = `conv_${Date.now()}`
      setConversationId(newConvId)
    }
  }, [userId, conversationId, setUserId, setConversationId])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const question = input.trim()
    setInput('')
    setIsLoading(true)

    // Add user message
    addMessage({
      text: question,
      isUser: true,
    })

    try {
      const response = await api.chat.sendMessage({
        question,
        user_id: userId || undefined,
        conversation_id: conversationId || undefined,
      })

      // Add bot response
      addMessage({
        text: response.answer,
        isUser: false,
        sources: response.context_sources,
      })

      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      addMessage({
        text: '????????, ????????? ??????. ?????????? ??? ???.',
        isUser: false,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <>
      <Head>
        <title>RAG Chatbot - AI ????????</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <div className="flex flex-col h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 px-4 py-3">
          <h1 className="text-xl font-semibold text-gray-800">AI ????????</h1>
          <p className="text-sm text-gray-500">??????? ?????? ? ???????? ??? ???????</p>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-20">
              <p className="text-lg mb-2">????? ??????????!</p>
              <p className="text-sm">??????? ???? ?????? ?????? ? ???????? ??? ???????.</p>
            </div>
          )}

          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white rounded-lg px-4 py-3 shadow-sm max-w-md">
                <Loader2 className="w-5 h-5 animate-spin text-primary-500" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="bg-white border-t border-gray-200 px-4 py-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="??????? ??? ??????..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              onClick={handleSend}
              disabled={isLoading || !input.trim()}
              className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

function MessageBubble({ message }: { message: Message }) {
  return (
    <div className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-md px-4 py-3 rounded-lg shadow-sm ${
          message.isUser
            ? 'bg-primary-500 text-white'
            : 'bg-white text-gray-800'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.text}</p>
        {message.sources && message.sources.length > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-200 text-xs opacity-75">
            <p>?????????:</p>
            <ul className="list-disc list-inside mt-1">
              {message.sources.map((source, idx) => (
                <li key={idx}>{source}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
