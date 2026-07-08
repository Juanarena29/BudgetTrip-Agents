import { Link } from 'react-router-dom'

export function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[var(--color-background)]">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(54,34,34,0.35),transparent_55%),radial-gradient(circle_at_80%_20%,rgba(66,63,62,0.18),transparent_35%)]"
      />

      <div className="relative mx-auto flex min-h-screen max-w-5xl flex-col px-4 py-8 sm:px-6">
        <header className="flex items-center justify-between">
          <p className="font-[family-name:var(--font-display)] text-lg font-semibold tracking-tight">
            BudgetTrip
          </p>
          <Link
            to="/chat"
            className="text-sm text-[var(--color-muted-foreground)] transition-colors hover:text-[var(--color-foreground)]"
          >
            Ir al chat
          </Link>
        </header>

        <main className="flex flex-1 flex-col justify-center py-16">
          <p className="mb-4 text-[0.6875rem] font-medium uppercase tracking-[0.18em] text-[var(--color-subtle-foreground)]">
            Planificador con agentes
          </p>
          <h1 className="max-w-3xl font-[family-name:var(--font-display)] text-4xl font-semibold leading-[1.05] tracking-tight sm:text-6xl">
            Contale tu viaje.
            <span className="block text-[var(--color-muted-foreground)]">Nosotros lo planificamos.</span>
          </h1>
          <p className="mt-6 max-w-xl text-base leading-relaxed text-[var(--color-muted-foreground)] sm:text-lg">
            Nuestros agentes de IA procesan tus ideas y las convierten en una ruta de viaje detallada,
            optimizando cada gasto de manera automática.
          </p>

          <div className="mt-10">
            <Link
              to="/chat"
              className="inline-flex w-full items-center justify-center rounded-[var(--radius-md)] border border-[var(--color-border-subtle)] bg-[var(--button-primary-bg)] px-5 py-2.5 text-sm font-medium text-[var(--color-primary-foreground)] transition-colors hover:bg-[var(--button-primary-hover)] sm:w-auto"
            >
              Empezar en el chat
            </Link>
          </div>

          <div className="mt-16 grid gap-4 sm:grid-cols-3">
            {[
              {
                title: 'Tu Idea',
                body: 'Contanos a dónde querés ir, tus fechas y cuánto querés gastar de la forma más natural. El sistema entiende todo al instante.',
              },
              {
                title: 'Búsqueda Inteligente',
                body: 'Nuestros agentes rastrean la web en tiempo real buscando los mejores precios, hospedajes y actividades low-cost para vos.',
              },
              {
                title: 'Itinerario Listo',
                body: 'Recibís un plan detallado día por día con costos estimados transparentes, optimizado para no pasarte de tu presupuesto.',
              },
            ].map((item) => (
              <article
                key={item.title}
                className="rounded-[var(--radius-xl)] border border-[var(--color-border-subtle)] bg-[var(--color-surface)]/70 p-5 backdrop-blur-sm"
              >
                <h2 className="font-[family-name:var(--font-display)] text-lg font-semibold">
                  {item.title}
                </h2>
                <p className="mt-2 text-sm leading-relaxed text-[var(--color-muted-foreground)]">
                  {item.body}
                </p>
              </article>
            ))}
          </div>
        </main>

        <footer className="border-t border-[var(--color-border-subtle)] pt-6 text-xs text-[var(--color-subtle-foreground)]">
          BudgetTrip · Agentic travel planning
        </footer>
      </div>
    </div>
  )
}
