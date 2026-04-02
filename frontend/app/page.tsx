'use client'

import { useState, useRef } from 'react'
import { ChatInterface } from '@/components/ChatInterface'
import { Sidebar } from '@/components/Sidebar'

export default function Home() {
    const [sessionId] = useState(`session_${Date.now()}`)
    const chatInterfaceRef = useRef<any>(null)

    const handleTemplateClick = (template: string) => {
        if (chatInterfaceRef.current) {
            chatInterfaceRef.current.setInputValue(template)
        }
    }

    return (
        <div className="flex h-screen bg-gray-100">
            <Sidebar sessionId={sessionId} onTemplateClick={handleTemplateClick} />
            <ChatInterface ref={chatInterfaceRef} sessionId={sessionId} />
        </div>
    )
}
