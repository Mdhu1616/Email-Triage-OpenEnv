"use client"

import { useState } from "react"

const codeExamples = [
  {
    id: "basic",
    title: "Basic Usage",
    filename: "example.py",
    code: `from env import EmailTriageEnv, grade_episode

# Initialize environment with a task
env = EmailTriageEnv(task_id="medium_triage")

# Reset with deterministic seed
obs = env.reset(seed=42)

# Agent interaction loop
while True:
    # Your agent decides on an action
    action = your_agent.decide(obs)
    
    # Step the environment
    obs, reward, done, info = env.step(action)
    
    if done:
        break

# Get final grading
result = grade_episode("medium_triage", env.state())
print(f"Score: {result['score']:.2f}")`,
  },
  {
    id: "action",
    title: "Action Types",
    filename: "actions.py",
    code: `from env import Action, ActionType, EmailCategory, EmailPriority

# Categorize an email
categorize = Action(
    action_type=ActionType.CATEGORIZE,
    category=EmailCategory.WORK
)

# Set priority level
priority = Action(
    action_type=ActionType.SET_PRIORITY,
    priority=EmailPriority.HIGH
)

# Flag for follow-up
flag = Action(action_type=ActionType.FLAG)

# Archive email
archive = Action(action_type=ActionType.ARCHIVE)

# Draft a reply
reply = Action(
    action_type=ActionType.REPLY,
    reply_content="Thank you for your message..."
)`,
  },
  {
    id: "grading",
    title: "Grading System",
    filename: "grading.py",
    code: `from env import grade_episode, get_all_tasks

# Get available tasks
tasks = get_all_tasks()
for task_id, config in tasks.items():
    print(f"{task_id}: {config.name}")
    print(f"  Difficulty: {config.difficulty}")
    print(f"  Threshold: {config.success_threshold}")

# Grade an episode after completion
result = grade_episode("hard_inbox_zero", env.state())

print(f"Score: {result['score']:.3f}")
print(f"Passed: {result['passed']}")
print(f"Breakdown: {result['breakdown']}")`,
  },
]

export function CodePreview() {
  const [activeTab, setActiveTab] = useState(codeExamples[0])
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(activeTab.code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <section id="quickstart" className="py-24 lg:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Quick Start
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Get up and running in minutes with our intuitive API.
          </p>
        </div>

        <div className="mt-12 overflow-hidden rounded-xl border border-border bg-card">
          {/* Tab header */}
          <div className="flex items-center justify-between border-b border-border bg-secondary/30 px-4">
            <div className="flex">
              {codeExamples.map((example) => (
                <button
                  key={example.id}
                  onClick={() => setActiveTab(example)}
                  className={`relative px-4 py-3 text-sm font-medium transition-colors ${
                    activeTab.id === example.id
                      ? "text-foreground"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {example.title}
                  {activeTab.id === example.id && (
                    <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent" />
                  )}
                </button>
              ))}
            </div>
            <button
              onClick={handleCopy}
              className="flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            >
              {copied ? (
                <>
                  <CheckIcon className="h-4 w-4 text-success" />
                  Copied
                </>
              ) : (
                <>
                  <CopyIcon className="h-4 w-4" />
                  Copy
                </>
              )}
            </button>
          </div>

          {/* File name bar */}
          <div className="flex items-center gap-2 border-b border-border bg-secondary/20 px-4 py-2">
            <FileIcon className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">{activeTab.filename}</span>
          </div>

          {/* Code content */}
          <div className="overflow-x-auto p-6">
            <pre className="text-sm leading-relaxed">
              <code>
                {activeTab.code.split("\n").map((line, i) => (
                  <div key={i} className="flex">
                    <span className="mr-6 inline-block w-6 select-none text-right text-muted-foreground/50">
                      {i + 1}
                    </span>
                    <span className="flex-1">{line || "\u00a0"}</span>
                  </div>
                ))}
              </code>
            </pre>
          </div>
        </div>

        {/* Installation steps */}
        <div className="mt-16 grid gap-6 md:grid-cols-3">
          <div className="rounded-xl border border-border bg-card p-6">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10 text-accent">
              <span className="text-lg font-bold">1</span>
            </div>
            <h3 className="mt-4 font-semibold">Install</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Install the package using pip or clone the repository.
            </p>
            <code className="mt-4 block rounded-lg bg-secondary/50 px-3 py-2 text-sm font-mono">
              pip install -e .
            </code>
          </div>

          <div className="rounded-xl border border-border bg-card p-6">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10 text-accent">
              <span className="text-lg font-bold">2</span>
            </div>
            <h3 className="mt-4 font-semibold">Validate</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Run the validation script to ensure everything works.
            </p>
            <code className="mt-4 block rounded-lg bg-secondary/50 px-3 py-2 text-sm font-mono">
              python scripts/validate_env.py
            </code>
          </div>

          <div className="rounded-xl border border-border bg-card p-6">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10 text-accent">
              <span className="text-lg font-bold">3</span>
            </div>
            <h3 className="mt-4 font-semibold">Run Baseline</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              Execute the baseline inference to see example scores.
            </p>
            <code className="mt-4 block rounded-lg bg-secondary/50 px-3 py-2 text-sm font-mono text-xs">
              python scripts/baseline_inference.py
            </code>
          </div>
        </div>
      </div>
    </section>
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

function FileIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  )
}
