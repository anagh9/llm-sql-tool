import './globals.css'
import type { Metadata } from 'next'
import { Providers } from './providers'

export const metadata: Metadata = {
    title: 'InsightBot Query Tool',
    description: 'Ask questions in natural language, get SQL results',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className="bg-gray-50 text-gray-900">
                <Providers>
                    {children}
                </Providers>
            </body>
        </html>
    )
}
