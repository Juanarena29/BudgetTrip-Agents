import { Link } from 'react-router-dom'

export function AppHeader() {
  return (
    <header className="border-b border-[var(--color-border-subtle)] bg-[var(--color-background)]/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link
          to="/"
          className="font-[family-name:var(--font-display)] text-lg font-semibold tracking-tight text-[var(--color-foreground)] transition-opacity hover:opacity-80"
        >
          BudgetTrip
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <Link
            to="/chat"
            className="text-[var(--color-muted-foreground)] transition-colors hover:text-[var(--color-foreground)]"
          >
            Chat
          </Link>
        </nav>
      </div>
    </header>
  )
}
