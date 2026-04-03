import type { Metadata } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'

const _geist = Geist({ subsets: ["latin"] });
const _geistMono = Geist_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: 'Email Triage OpenEnv | AI Agent Training Environment',
  description: 'A reproducible environment for training and benchmarking AI agents on real-world email triage tasks. OpenEnv v1.0 specification compliant.',
  generator: 'v0.app',
  keywords: ['OpenEnv', 'AI', 'agent training', 'email triage', 'LLM', 'RLHF', 'benchmark'],
  openGraph: {
    title: 'Email Triage OpenEnv',
    description: 'Train AI agents on real-world email tasks',
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
