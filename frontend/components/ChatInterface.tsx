'use client'

import { useState, useEffect, useRef, forwardRef, useImperativeHandle } from 'react'
import { FiSend, FiLoader } from 'react-icons/fi'
import { sendMessage, ChartData } from '@/lib/api'
import { Line, Pie, Bar } from 'react-chartjs-2'
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js'

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    ArcElement,
    Title,
    Tooltip,
    Legend
)

interface Message {
    role: 'user' | 'assistant'
    content: string
    timestamp: string
    visualise?: boolean
    chart_type?: 'line' | 'pie' | 'bar'
    chart_data?: ChartData
}

interface ChatInterfaceRef {
    setInputValue: (value: string) => void
}

// Chart Renderer Component for Dynamic Chart Rendering
function ChartRenderer({
    chartType,
    chartData,
    datasetCount = 1
}: {
    chartType: 'line' | 'pie' | 'bar'
    chartData: ChartData
    datasetCount?: number
}) {
    if (!chartData || !chartData.datasets || chartData.datasets.length === 0) {
        return (
            <div className="mt-4 bg-gray-50 rounded-lg p-4 text-center text-gray-500">
                Unable to generate chart - no data available
            </div>
        )
    }

    // Dynamic chart options based on data and type
    const getChartOptions = () => {
        const baseOptions = {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: chartType === 'bar' ? ('x' as const) : undefined,
        } as any

        if (chartType === 'line') {
            return {
                ...baseOptions,
                plugins: {
                    filler: {
                        propagate: true,
                    },
                    legend: {
                        position: 'top' as const,
                        display: datasetCount > 1,
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            font: {
                                size: 12,
                                weight: '500' as const,
                            }
                        }
                    },
                    title: {
                        display: datasetCount > 1,
                        text: `${datasetCount} Dataset(s)`,
                        font: {
                            size: 14,
                            weight: 'bold' as const,
                        },
                        padding: {
                            top: 10,
                            bottom: 30
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: {
                            size: 13,
                            weight: 'bold' as const,
                        },
                        bodyFont: {
                            size: 12,
                        },
                        cornerRadius: 4,
                        displayColors: true,
                        callbacks: {
                            label: function (context: any) {
                                let value = context.parsed.y
                                if (typeof value === 'number') {
                                    if (value >= 1000000) return context.dataset.label + ': $' + (value / 1000000).toFixed(1) + 'M'
                                    if (value >= 1000) return context.dataset.label + ': $' + (value / 1000).toFixed(1) + 'K'
                                    return context.dataset.label + ': $' + value.toLocaleString()
                                }
                                return context.dataset.label + ': ' + value
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: true,
                        },
                        ticks: {
                            callback: function (value: any) {
                                if (value >= 1000000) return '$' + (value / 1000000).toFixed(1) + 'M'
                                if (value >= 1000) return '$' + (value / 1000).toFixed(1) + 'K'
                                return '$' + value.toFixed(0)
                            },
                            font: {
                                size: 11,
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false,
                        },
                        ticks: {
                            font: {
                                size: 11,
                            }
                        }
                    }
                }
            }
        } else if (chartType === 'pie') {
            return {
                ...baseOptions,
                plugins: {
                    legend: {
                        position: 'bottom' as const,
                        display: true,
                        labels: {
                            padding: 15,
                            font: {
                                size: 12,
                            },
                            usePointStyle: true,
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: {
                            size: 13,
                            weight: 'bold' as const,
                        },
                        bodyFont: {
                            size: 12,
                        },
                        cornerRadius: 4,
                        callbacks: {
                            label: function (context: any) {
                                const value = context.parsed
                                const total = context.dataset.data.reduce((a: number, b: number) => a + b, 0)
                                const percentage = ((value / total) * 100).toFixed(1)
                                return `${context.label}: $${value.toLocaleString()} (${percentage}%)`
                            }
                        }
                    }
                }
            }
        } else { // bar
            return {
                ...baseOptions,
                plugins: {
                    legend: {
                        position: 'top' as const,
                        display: datasetCount > 1,
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            font: {
                                size: 12,
                                weight: '500' as const,
                            }
                        }
                    },
                    title: {
                        display: datasetCount > 1,
                        text: `${datasetCount} Dataset(s)`,
                        font: {
                            size: 14,
                            weight: 'bold' as const,
                        },
                        padding: {
                            top: 10,
                            bottom: 30
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: {
                            size: 13,
                            weight: 'bold' as const,
                        },
                        bodyFont: {
                            size: 12,
                        },
                        cornerRadius: 4,
                        displayColors: true,
                        callbacks: {
                            label: function (context: any) {
                                let value = context.parsed.y
                                if (typeof value === 'number') {
                                    if (value >= 1000000) return context.dataset.label + ': $' + (value / 1000000).toFixed(1) + 'M'
                                    if (value >= 1000) return context.dataset.label + ': $' + (value / 1000).toFixed(1) + 'K'
                                    return context.dataset.label + ': $' + value.toLocaleString()
                                }
                                return context.dataset.label + ': ' + value
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: true,
                        },
                        ticks: {
                            callback: function (value: any) {
                                if (value >= 1000000) return '$' + (value / 1000000).toFixed(1) + 'M'
                                if (value >= 1000) return '$' + (value / 1000).toFixed(1) + 'K'
                                return '$' + value.toFixed(0)
                            },
                            font: {
                                size: 11,
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false,
                        },
                        ticks: {
                            font: {
                                size: 11,
                            }
                        }
                    }
                }
            }
        }
    }

    // Determine container height based on data complexity
    const getContainerHeight = () => {
        const dataPoints = chartData.labels?.length || 0
        const hasMultipleDatasets = (chartData.datasets?.length || 0) > 1

        if (chartType === 'pie') {
            return dataPoints > 5 ? '380px' : '340px'
        }
        if (hasMultipleDatasets) {
            return dataPoints > 15 ? '450px' : 'auto'
        }
        if (dataPoints > 15) return '400px'
        if (dataPoints > 10) return '350px'
        return '300px'
    }

    // Determine container width
    const getContainerWidth = () => {
        const dataPoints = chartData.labels?.length || 0
        if (chartType === 'pie') return '100%'
        if (dataPoints > 15) return '100%'
        return '100%'
    }

    return (
        <div
            className="mt-4 bg-gradient-to-br from-white to-gray-50 rounded-lg p-6 shadow-md border border-gray-200 hover:shadow-lg transition-shadow duration-200"
            style={{
                minHeight: getContainerHeight(),
                width: getContainerWidth(),
                maxWidth: '100%'
            }}
        >
            {chartType === 'line' && (
                <Line
                    data={chartData}
                    options={getChartOptions()}
                />
            )}
            {chartType === 'pie' && (
                <Pie
                    data={chartData}
                    options={getChartOptions()}
                />
            )}
            {chartType === 'bar' && (
                <Bar
                    data={chartData}
                    options={getChartOptions()}
                />
            )}
        </div>
    )
}

export const ChatInterface = forwardRef<ChatInterfaceRef, { sessionId: string }>(
    function ChatInterface({ sessionId }, ref) {
        const [messages, setMessages] = useState<Message[]>([])
        const [input, setInput] = useState('')
        const [loading, setLoading] = useState(false)
        const messagesEndRef = useRef<HTMLDivElement>(null)

        // Expose setInputValue method via ref
        useImperativeHandle(ref, () => ({
            setInputValue: (value: string) => {
                setInput(value)
            }
        }))

        const scrollToBottom = () => {
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
        }

        useEffect(() => {
            scrollToBottom()
        }, [messages])

        const handleSendMessage = async () => {
            if (!input.trim() || loading) return

            const userMessage = input.trim()
            setInput('')

            // Add user message
            const newUserMessage: Message = {
                role: 'user',
                content: userMessage,
                timestamp: new Date().toISOString(),
            }
            setMessages((prev) => [...prev, newUserMessage])

            setLoading(true)
            try {
                const response = await sendMessage(userMessage, sessionId)

                const assistantMessage: Message = {
                    role: 'assistant',
                    content: response.answer,
                    timestamp: response.timestamp,
                    visualise: response.visualise || false,
                    chart_type: response.chart_type,
                    chart_data: response.chart_data,
                }
                setMessages((prev) => [...prev, assistantMessage])
            } catch (error) {
                console.error('Error sending message:', error)
                const errorMessage: Message = {
                    role: 'assistant',
                    content: 'Sorry, there was an error processing your request.',
                    timestamp: new Date().toISOString(),
                }
                setMessages((prev) => [...prev, errorMessage])
            } finally {
                setLoading(false)
            }
        }

        const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSendMessage()
            }
        }

        return (
            <div className="flex flex-col flex-1">
                {/* Header */}
                <div className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
                    <h1 className="text-2xl font-bold text-gray-900">InsightBot Chat</h1>
                    <p className="text-sm text-gray-600 mt-1">Ask questions in natural language about your database</p>
                </div>

                {/* Messages Container */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                    {messages.length === 0 ? (
                        <div className="flex items-center justify-center h-full">
                            <div className="text-center">
                                <div className="text-6xl mb-4">💬</div>
                                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                                    Start a Conversation
                                </h2>
                                <p className="text-gray-600">
                                    Ask any question about your database and get instant SQL-generated answers
                                </p>
                            </div>
                        </div>
                    ) : (
                        <>
                            {messages.map((message, index) => (
                                <div
                                    key={index}
                                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'
                                        }`}
                                >
                                    <div
                                        className={`${message.role === 'user'
                                            ? 'bg-blue-500 text-white rounded-br-none'
                                            : 'bg-gray-100 text-gray-900 rounded-bl-none'
                                            } px-4 py-3 rounded-lg max-w-2xl`}
                                    >
                                        <p className="text-sm break-words whitespace-pre-wrap">{message.content}</p>

                                        {/* Chart Visualization - Dynamic Rendering */}
                                        {message.visualise && message.chart_data && message.chart_type && (
                                            <ChartRenderer
                                                chartType={message.chart_type}
                                                chartData={message.chart_data}
                                                datasetCount={message.chart_data.datasets?.length || 0}
                                            />
                                        )}

                                        <p className="text-xs opacity-70 mt-2">
                                            {new Date(message.timestamp).toLocaleTimeString()}
                                        </p>
                                    </div>
                                </div>
                            ))}
                            {loading && (
                                <div className="flex justify-start">
                                    <div className="bg-gray-100 text-gray-900 px-4 py-3 rounded-lg rounded-bl-none">
                                        <FiLoader className="animate-spin" />
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </>
                    )}
                </div>

                {/* Input Area */}
                <div className="bg-white border-t border-gray-200 p-6">
                    <div className="flex gap-3">
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Ask a question... (Shift+Enter for new line)"
                            disabled={loading}
                            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                            rows={3}
                        />
                        <button
                            onClick={handleSendMessage}
                            disabled={loading || !input.trim()}
                            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                        >
                            {loading ? (
                                <FiLoader className="animate-spin" />
                            ) : (
                                <>
                                    <FiSend /> Send
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        )
    }
)
