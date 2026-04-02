'use client'

import { useState, useRef, useEffect } from 'react'
import { ChatInterface } from '@/components/ChatInterface'
import { Sidebar } from '@/components/Sidebar'

export default function Home() {
    const [sessionId] = useState(`session_${Date.now()}`)

    return (
        <div className="flex h-screen bg-gray-100">
            <Sidebar sessionId={sessionId} />
            <ChatInterface sessionId={sessionId} />
        </div>
    )
}
