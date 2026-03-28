"use client"

import { useState } from "react"

export function Hero() {
  const [copied, setCopied] = useState(false)
  const installCommand = "pip install -e ."

  const handleCopy = async () => {
    await navigator.clipboard.writeText(installCommand)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <section className="relative overflow-hidden pt-32 pb-20 lg:pt-40 lg:pb-32">
      {/* Background gradient effect */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-0 -translate-x-1/2 -translate-y-1/2 h-[600px] w-[600px] rounded-full bg-accent/20 blur-[120px]" />
      </div>

      <div className="relative mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          {/* Badge */}
          <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-border bg-secondary/50 px-4 py-1.5">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-accent" />
            </span>
            <span className="text-sm text-muted-foreground">OpenEnv v1.0 Spec Compliant</span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl lg:text-7xl">
            <span className="text-balance">Train AI agents on</span>
            <br />
            <span className="text-balance bg-gradient-to-r from-accent to-accent/60 bg-clip-text text-transparent">
              real-world email tasks
            </span>
          </h1>

          {/* Subheadline */}
          <p className="mt-6 text-lg leading-relaxed text-muted-foreground sm:text-xl">
            A reproducible environment for benchmarking LLM agents on email triage, 
            categorization, and response generation. Fully typed, deterministically seeded, 
            and ready for RLHF training.
          </p>

          {/* CTA Buttons */}
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <a
              href="#quickstart"
              className="inline-flex h-12 items-center justify-center rounded-lg bg-primary px-8 text-sm font-medium text-primary-foreground transition-all hover:bg-primary/90 hover:scale-[1.02]"
            >
              Get Started
              <ArrowRightIcon className="ml-2 h-4 w-4" />
            </a>

            {/* Install command */}
            <button
              onClick={handleCopy}
              className="group inline-flex h-12 items-center gap-3 rounded-lg border border-border bg-secondary/50 px-4 font-mono text-sm transition-all hover:border-accent/50 hover:bg-secondary"
            >
              <span className="text-muted-foreground">$</span>
              <span>{installCommand}</span>
              {copied ? (
                <CheckIcon className="h-4 w-4 text-success" />
              ) : (
                <CopyIcon className="h-4 w-4 text-muted-foreground transition-colors group-hover:text-foreground" />
              )}
            </button>
          </div>

          {/* Stats */}
          <div className="mt-16 grid grid-cols-3 gap-8 border-t border-border pt-8">
            <div>
              <div className="text-3xl font-bold tabular-nums">3</div>
              <div className="mt-1 text-sm text-muted-foreground">Task Difficulties</div>
            </div>
            <div>
              <div className="text-3xl font-bold tabular-nums">100%</div>
              <div className="mt-1 text-sm text-muted-foreground">Reproducible</div>
            </div>
            <div>
              <div className="text-3xl font-bold tabular-nums">Typed</div>
              <div className="mt-1 text-sm text-muted-foreground">Pydantic Models</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function ArrowRightIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
    </svg>
  )
}

function CopyIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
  )
}

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
    </svg>
  )
}
