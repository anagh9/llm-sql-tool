'use client'

import { useState, useEffect } from 'react'
import { FiMenu, FiX, FiSettings, FiBarChart2, FiClock } from 'react-icons/fi'
import { getSuggestions, getStats, clearHistory } from '@/lib/api'

export function Sidebar({ sessionId, onTemplateClick, onHistoryClick }: { sessionId: string; onTemplateClick?: (template: string) => void; onHistoryClick?: () => void }) {
    const [isOpen, setIsOpen] = useState(false)
    const [suggestions, setSuggestions] = useState<string[]>([])
    const [stats, setStats] = useState<any>(null)
    const [loading, setLoading] = useState(true)

    // Graph-related templates
    const graphTemplates = [
        'Show me orders every month',
        'Display revenue trend by quarter',
        'Compare sales across regions with chart',
        'What percentage of orders are completed vs pending?',
        'Show top 10 products by volume',
        'Average order value by category chart',
        'Create a graph of daily transactions',
        'Show customer distribution by region as pie chart',
        'What is the monthly growth rate trend?',
        'Display inventory levels over time'
    ]

    useEffect(() => {
        loadSuggestions()
        loadStats()
    }, [])

    const loadSuggestions = async () => {
        try {
            const response = await getSuggestions()
            // Combine API suggestions with graph templates
            const combined = [...graphTemplates, ...response.suggestions]
            setSuggestions(combined.slice(0, 10)) // Limit to 10 templates
        } catch (error) {
            console.error('Error loading suggestions:', error)
            // Use graph templates as fallback
            setSuggestions(graphTemplates.slice(0, 10))
        }
    }

    const loadStats = async () => {
        try {
            const response = await getStats()
            setStats(response)
        } catch (error) {
            console.error('Error loading stats:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleClearHistory = async () => {
        if (confirm('Are you sure you want to clear the history?')) {
            try {
                await clearHistory(sessionId)
                window.location.reload()
            } catch (error) {
                console.error('Error clearing history:', error)
            }
        }
    }

    return (
        <>
            {/* Mobile Menu Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="lg:hidden fixed top-6 left-4 z-50 p-2 bg-blue-500 text-white rounded-lg"
            >
                {isOpen ? <FiX size={24} /> : <FiMenu size={24} />}
            </button>

            {/* Sidebar */}
            <aside
                className={`w-80 bg-white border-r border-gray-200 p-6 overflow-y-auto transition-transform duration-300 fixed lg:static h-full z-40 lg:z-auto
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
            >
                {/* Header */}
                <div className="mb-8 mt-16 lg:mt-0">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center text-white font-bold">
                            💾
                        </div>
                        <h2 className="text-xl font-bold text-gray-900">InsightBot</h2>
                    </div>
                    <p className="text-xs text-gray-600">Query Assistant</p>
                </div>

                {/* Quick Templates */}
                <div className="mb-8">
                    <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <FiBarChart2 size={16} />
                        Quick Templates
                    </h3>
                    <div className="space-y-2">
                        {suggestions.map((suggestion, index) => (
                            <button
                                key={index}
                                onClick={() => {
                                    onTemplateClick?.(suggestion)
                                    setIsOpen(false)
                                }}
                                className="w-full text-left text-sm px-3 py-2 rounded-lg bg-gradient-to-r from-blue-50 to-cyan-50 hover:from-blue-100 hover:to-cyan-100 text-gray-700 transition-all duration-200 truncate border border-blue-100 hover:border-blue-300"
                                title={suggestion}
                            >
                                <span className="text-blue-600 mr-2">📊</span>
                                {suggestion}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Statistics */}
                {!loading && stats && (
                    <div className="mb-8">
                        <h3 className="text-sm font-semibold text-gray-900 mb-4">Statistics</h3>
                        <div className="space-y-3 bg-gray-50 p-4 rounded-lg">
                            <div>
                                <p className="text-xs text-gray-600">Total Conversations</p>
                                <p className="text-lg font-bold text-gray-900">
                                    {stats.total_conversations}
                                </p>
                            </div>
                            <div>
                                <p className="text-xs text-gray-600">Total Queries</p>
                                <p className="text-lg font-bold text-gray-900">
                                    {stats.total_queries}
                                </p>
                            </div>
                            <div>
                                <p className="text-xs text-gray-600">Cached Queries</p>
                                <p className="text-lg font-bold text-gray-900">
                                    {stats.total_cached_queries}
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Actions */}
                <div className="space-y-2">
                    <button
                        onClick={() => {
                            onHistoryClick?.()
                            setIsOpen(false)
                        }}
                        className="w-full px-3 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition-colors flex items-center justify-center gap-2"
                    >
                        <FiClock size={16} />
                        View History
                    </button>
                    <button
                        onClick={handleClearHistory}
                        className="w-full px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                        Clear History
                    </button>
                </div>
            </aside>

            {/* Overlay for Mobile */}
            {isOpen && (
                <div
                    onClick={() => setIsOpen(false)}
                    className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
                />
            )}
        </>
    )
}
