import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'

const _geist = Geist({ subsets: ["latin"] });
const _geistMono = Geist_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: 'Email Manager | Smart Email Organization',
  description: 'Intelligent email management system for categorizing and organizing your inbox with automated prioritization.',
  generator: 'v0.app',
  keywords: ['email', 'triage', 'organization', 'productivity', 'automation'],
  openGraph: {
    title: 'Email Manager',
    description: 'Smart email organization and categorization system',
    type: 'website',
  },
  icons: {
    icon: [
      {
        url: '/Logo.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/Logo.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/Logo.png',
        type: 'image/svg+xml',
      },
    ],
    apple: '/Logo.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="font-sans antialiased selection:bg-accent/20 selection:text-accent-foreground">
        {children}
        <Analytics />
      </body>
    </html>
  )
}
