import { Header } from "@/components/header"
import { Hero } from "@/components/hero"
import { TasksSection } from "@/components/tasks-section"
import { FeaturesSection } from "@/components/features-section"
import { CodePreview } from "@/components/code-preview"
import { Footer } from "@/components/footer"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>
        <Hero />
        <TasksSection />
        <FeaturesSection />
        <CodePreview />
      </main>
      <Footer />
    </div>
  )
}
