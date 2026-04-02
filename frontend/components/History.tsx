'use client'

import { useState, useEffect } from 'react'
import { FiX, FiTrendingUp, FiPieChart, FiBarChart2, FiClock, FiTrash2, FiRefreshCw } from 'react-icons/fi'
import { getSessionHistoryDB, deleteSessionHistoryDB, HistoryRecord } from '@/lib/api'

interface HistoryProps {
    sessionId: string
    isOpen: boolean
    onClose: () => void
    onSelectQuery?: (question: string) => void
}

export function History({ sessionId, isOpen, onClose, onSelectQuery }: HistoryProps) {
    const [history, setHistory] = useState<HistoryRecord[]>([])
    const [loading, setLoading] = useState(false)
    const [filter, setFilter] = useState<'all' | 'visualized' | 'cached'>('all')

    useEffect(() => {
        if (isOpen) {
            loadHistory()
        }
    }, [isOpen, sessionId])

    const loadHistory = async () => {
        setLoading(true)
        try {
            const response = await getSessionHistoryDB(sessionId, 100)
            if (response.success) {
                setHistory(response.history)
            }
        } catch (error) {
            console.error('Error loading history:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleDeleteHistory = async () => {
        if (confirm('Are you sure you want to delete all history for this session?')) {
            try {
                await deleteSessionHistoryDB(sessionId)
                setHistory([])
                console.log('History deleted successfully')
            } catch (error) {
                console.error('Error deleting history:', error)
            }
        }
    }

    const getChartIcon = (chartType?: string) => {
        switch (chartType) {
            case 'line':
                return <FiTrendingUp className="w-4 h-4 text-blue-500" />
            case 'pie':
                return <FiPieChart className="w-4 h-4 text-purple-500" />
            case 'bar':
                return <FiBarChart2 className="w-4 h-4 text-green-500" />
            default:
                return null
        }
    }

    const formatDate = (dateString: string) => {
        const date = new Date(dateString)
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    let filteredHistory = history
    if (filter === 'visualized') {
        filteredHistory = history.filter(item => item.visualise)
    } else if (filter === 'cached') {
        filteredHistory = history.filter(item => item.cached)
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-50 overflow-hidden">
            {/* Backdrop */}
            <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />

            {/* Slide-over panel */}
            <div className="fixed right-0 top-0 max-w-2xl w-full h-full bg-white shadow-xl flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-cyan-50">
                    <div>
                        <h2 className="text-xl font-bold text-gray-900">Query History</h2>
                        <p className="text-sm text-gray-600">Session: {sessionId.substring(8, 12)}</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                        <FiX size={24} />
                    </button>
                </div>

                {/* Filter Tabs */}
                <div className="flex gap-2 px-6 py-4 border-b border-gray-200">
                    <button
                        onClick={() => setFilter('all')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${filter === 'all'
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        All ({history.length})
                    </button>
                    <button
                        onClick={() => setFilter('visualized')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${filter === 'visualized'
                            ? 'bg-purple-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        Visualized ({history.filter(h => h.visualise).length})
                    </button>
                    <button
                        onClick={() => setFilter('cached')}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${filter === 'cached'
                            ? 'bg-green-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        Cached ({history.filter(h => h.cached).length})
                    </button>
                </div>

                {/* History List */}
                <div className="flex-1 overflow-y-auto p-6 space-y-3">
                    {loading ? (
                        <div className="flex items-center justify-center h-full">
                            <div className="text-center">
                                <FiRefreshCw className="animate-spin mx-auto mb-2 w-8 h-8 text-blue-500" />
                                <p className="text-gray-600">Loading history...</p>
                            </div>
                        </div>
                    ) : filteredHistory.length === 0 ? (
                        <div className="flex items-center justify-center h-full">
                            <div className="text-center text-gray-500">
                                <FiClock className="mx-auto mb-2 w-12 h-12 opacity-30" />
                                <p>No queries found</p>
                            </div>
                        </div>
                    ) : (
                        filteredHistory.map((record, index) => (
                            <div
                                key={record.id}
                                className="p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer group"
                                onClick={() => {
                                    onSelectQuery?.(record.question)
                                    onClose()
                                }}
                            >
                                {/* Question */}
                                <div className="flex items-start gap-3 mb-2">
                                    <div className="flex items-center gap-2">
                                        {record.visualise && getChartIcon(record.chart_type)}
                                        {record.cached && (
                                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                                Cached
                                            </span>
                                        )}
                                    </div>
                                    <p className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors">
                                        {record.question}
                                    </p>
                                </div>

                                {/* Answer Preview */}
                                <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                                    {record.answer}
                                </p>

                                {/* Metadata */}
                                <div className="flex items-center justify-between text-xs text-gray-500">
                                    <div className="flex items-center gap-2">
                                        <FiClock size={12} />
                                        <span>{formatDate(record.created_at)}</span>
                                    </div>
                                    {record.visualise && (
                                        <span className="text-xs font-medium text-purple-600 bg-purple-50 px-2 py-1 rounded">
                                            {record.chart_type?.toUpperCase()} Chart
                                        </span>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Footer Actions */}
                {history.length > 0 && (
                    <div className="border-t border-gray-200 px-6 py-4 flex gap-2 bg-gray-50">
                        <button
                            onClick={loadHistory}
                            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors font-medium"
                        >
                            <FiRefreshCw size={16} />
                            Refresh
                        </button>
                        <button
                            onClick={handleDeleteHistory}
                            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-100 text-red-600 rounded-lg hover:bg-red-200 transition-colors font-medium"
                        >
                            <FiTrash2 size={16} />
                            Clear History
                        </button>
                    </div>
                )}
            </div>
        </div>
    )
}
