'use client'

import { useState, useRef } from 'react'
import { ChatInterface } from '@/components/ChatInterface'
import { Sidebar } from '@/components/Sidebar'
import { History } from '@/components/History'

export default function Home() {
    const [sessionId] = useState(`session_${Date.now()}`)
    const [historyOpen, setHistoryOpen] = useState(false)
    const chatInterfaceRef = useRef<any>(null)

    const handleTemplateClick = (template: string) => {
        if (chatInterfaceRef.current) {
            chatInterfaceRef.current.setInputValue(template)
        }
    }

    const handleSelectFromHistory = (question: string) => {
        if (chatInterfaceRef.current) {
            chatInterfaceRef.current.setInputValue(question)
        }
    }

    return (
        <div className="flex h-screen bg-gray-100">
            <Sidebar
                sessionId={sessionId}
                onTemplateClick={handleTemplateClick}
                onHistoryClick={() => setHistoryOpen(true)}
            />
            <ChatInterface ref={chatInterfaceRef} sessionId={sessionId} />
            <History
                sessionId={sessionId}
                isOpen={historyOpen}
                onClose={() => setHistoryOpen(false)}
                onSelectQuery={handleSelectFromHistory}
            />
        </div>
    )
}
