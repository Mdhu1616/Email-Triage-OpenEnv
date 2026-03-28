"use client"

import { useState } from "react"

const tasks = [
  {
    id: "easy",
    title: "Easy Categorization",
    badge: "Beginner",
    description: "Classify emails into basic categories. Perfect for testing foundational agent capabilities.",
    emails: 5,
    categories: ["Work", "Personal", "Promotional"],
    scoring: "Accuracy-based",
    metrics: [
      { label: "Emails", value: "5" },
      { label: "Categories", value: "3" },
      { label: "Timeout", value: "60s" },
    ],
    features: [
      "Simple classification task",
      "Clear category boundaries",
      "Basic reward signal",
    ],
    color: "text-success",
    bgColor: "bg-success/10",
    borderColor: "border-success/20",
  },
  {
    id: "medium",
    title: "Medium Triage",
    badge: "Intermediate",
    description: "Handle spam detection, priority assignment, and multi-label categorization.",
    emails: 10,
    categories: ["Work", "Personal", "Promotional", "Spam"],
    scoring: "Weighted composite",
    metrics: [
      { label: "Emails", value: "10" },
      { label: "Priorities", value: "3" },
      { label: "Timeout", value: "120s" },
    ],
    features: [
      "Spam detection required",
      "Priority level assignment",
      "Weighted scoring system",
    ],
    color: "text-warning",
    bgColor: "bg-warning/10",
    borderColor: "border-warning/20",
  },
  {
    id: "hard",
    title: "Hard Inbox Zero",
    badge: "Advanced",
    description: "Full inbox management with replies, urgent handling, and efficiency optimization.",
    emails: 20,
    categories: ["Work", "Personal", "Promotional", "Spam", "Urgent"],
    scoring: "Multi-factor with bonuses",
    metrics: [
      { label: "Emails", value: "20" },
      { label: "Actions", value: "5+" },
      { label: "Timeout", value: "300s" },
    ],
    features: [
      "Draft reply generation",
      "Urgent email detection",
      "Efficiency bonus scoring",
      "False positive penalties",
    ],
    color: "text-destructive",
    bgColor: "bg-destructive/10",
    borderColor: "border-destructive/20",
  },
]

export function TasksSection() {
  const [selectedTask, setSelectedTask] = useState(tasks[1])

  return (
    <section id="tasks" className="py-24 lg:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Progressive difficulty levels
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Three carefully designed tasks that scale from basic classification to full inbox management.
          </p>
        </div>

        {/* Task selector tabs */}
        <div className="mt-12 flex justify-center">
          <div className="inline-flex rounded-lg border border-border bg-secondary/30 p-1">
            {tasks.map((task) => (
              <button
                key={task.id}
                onClick={() => setSelectedTask(task)}
                className={`rounded-md px-4 py-2 text-sm font-medium transition-all ${
                  selectedTask.id === task.id
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {task.title}
              </button>
            ))}
          </div>
        </div>

        {/* Selected task detail */}
        <div className="mt-12">
          <div className={`rounded-2xl border ${selectedTask.borderColor} bg-card p-8 lg:p-12`}>
            <div className="grid gap-8 lg:grid-cols-2">
              {/* Left column */}
              <div>
                <div className="flex items-center gap-3">
                  <span className={`inline-flex rounded-full px-3 py-1 text-xs font-medium ${selectedTask.bgColor} ${selectedTask.color}`}>
                    {selectedTask.badge}
                  </span>
                </div>
                <h3 className="mt-4 text-2xl font-bold">{selectedTask.title}</h3>
                <p className="mt-3 text-muted-foreground leading-relaxed">
                  {selectedTask.description}
                </p>

                {/* Metrics */}
                <div className="mt-8 grid grid-cols-3 gap-4">
                  {selectedTask.metrics.map((metric) => (
                    <div key={metric.label} className="rounded-lg border border-border bg-secondary/30 p-4 text-center">
                      <div className="text-xl font-bold">{metric.value}</div>
                      <div className="mt-1 text-xs text-muted-foreground">{metric.label}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Right column */}
              <div>
                <h4 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                  Task Requirements
                </h4>
                <ul className="mt-4 space-y-3">
                  {selectedTask.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3">
                      <CheckCircleIcon className={`mt-0.5 h-5 w-5 shrink-0 ${selectedTask.color}`} />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <div className="mt-8">
                  <h4 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                    Categories
                  </h4>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {selectedTask.categories.map((category) => (
                      <span
                        key={category}
                        className="rounded-full border border-border bg-secondary/50 px-3 py-1 text-sm"
                      >
                        {category}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-6">
                  <h4 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                    Scoring
                  </h4>
                  <p className="mt-2 text-sm">{selectedTask.scoring}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Task cards grid - smaller version */}
        <div className="mt-12 grid gap-4 md:grid-cols-3">
          {tasks.map((task) => (
            <button
              key={task.id}
              onClick={() => setSelectedTask(task)}
              className={`rounded-xl border p-6 text-left transition-all hover:border-accent/50 ${
                selectedTask.id === task.id
                  ? `${task.borderColor} bg-card`
                  : "border-border bg-card/50"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${task.bgColor} ${task.color}`}>
                  {task.badge}
                </span>
                <span className="text-sm text-muted-foreground">{task.emails} emails</span>
              </div>
              <h4 className="mt-3 font-semibold">{task.title}</h4>
            </button>
          ))}
        </div>
      </div>
    </section>
  )
}

function CheckCircleIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  )
}
