import type { DayPlan, Itinerary } from '@/types/api'
import { formatLocalDate } from '@/lib/dates'

interface ItineraryDayCardProps {
  day: DayPlan
}

function formatDate(value: string): string {
  return formatLocalDate(value, {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  })
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(value)
}

export function ItineraryDayCard({ day }: ItineraryDayCardProps) {
  return (
    <article
      className="w-full rounded-[var(--radius-lg)] border border-[var(--color-border-subtle)] bg-[var(--color-background)] p-5 transition-colors duration-200 hover:border-[var(--color-cream-300)]/40"
    >
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <p className="text-[0.6875rem] font-medium uppercase tracking-[0.14em] text-[var(--color-subtle-foreground)]">
            Día {day.day}
          </p>
          <h4 className="mt-1 font-[family-name:var(--font-display)] text-lg font-semibold leading-tight">
            {day.summary}
          </h4>
        </div>
        <div className="text-right text-sm">
          <p className="text-[var(--color-subtle-foreground)]">{formatDate(day.date)}</p>
          <p className="font-medium text-[var(--color-foreground)]">{formatCurrency(day.day_total)}</p>
        </div>
      </div>

      {day.activities.length > 0 && (
        <ul className="mb-4 space-y-1.5 text-sm text-[var(--color-muted-foreground)]">
          {day.activities.map((activity) => (
            <li key={activity} className="flex gap-2">
              <span className="text-[var(--color-subtle-foreground)]">·</span>
              <span>{activity}</span>
            </li>
          ))}
        </ul>
      )}

      {day.cost_items.length > 0 && (
        <div className="border-t border-[var(--color-border-subtle)] pt-3">
          <p className="mb-2 text-[0.6875rem] uppercase tracking-[0.1em] text-[var(--color-subtle-foreground)]">
            Costos
          </p>
          <ul className="space-y-1.5 text-sm">
            {day.cost_items.map((item) => (
              <li
                key={`${item.day}-${item.description}`}
                className="flex items-start justify-between gap-2 text-[var(--color-muted-foreground)]"
              >
                <span className="min-w-0">
                  <span className="text-[var(--color-subtle-foreground)]">{item.category}</span>
                  {' · '}
                  {item.description}
                </span>
                <span className="shrink-0">{formatCurrency(item.estimated_cost)}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </article>
  )
}

interface ItineraryModalProps {
  itinerary: Itinerary
  tripId: string
  open: boolean
  onClose: () => void
}

export function ItineraryModal({ itinerary, tripId, open, onClose }: ItineraryModalProps) {
  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-[var(--color-espresso-900)]/85 p-4 backdrop-blur-sm"
      onClick={onClose}
      role="presentation"
    >
      <div
        className="flex max-h-[88vh] w-full max-w-6xl flex-col overflow-hidden rounded-[var(--radius-xl)] border border-[var(--card-border)] bg-[var(--color-surface)] shadow-[var(--shadow-soft)]"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="itinerary-modal-title"
      >
        <header className="flex shrink-0 items-start justify-between gap-4 border-b border-[var(--color-border-subtle)] px-6 py-5">
          <div>
            <p className="text-[0.6875rem] font-medium uppercase tracking-[0.14em] text-[var(--color-subtle-foreground)]">
              Itinerario listo
            </p>
            <h2
              id="itinerary-modal-title"
              className="mt-1 font-[family-name:var(--font-display)] text-2xl font-semibold"
            >
              {itinerary.destination}
            </h2>
            <p className="mt-2 max-w-2xl text-sm text-[var(--color-muted-foreground)]">
              {itinerary.short_summary}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-[var(--color-subtle-foreground)]">Total estimado</p>
            <p className="font-[family-name:var(--font-display)] text-2xl font-semibold">
              {formatCurrency(itinerary.total_cost)}
            </p>
            <p
              className={`mt-1 text-xs ${
                itinerary.over_budget ? 'text-[var(--color-warning)]' : 'text-[var(--color-success)]'
              }`}
            >
              {itinerary.over_budget
                ? `Excede el presupuesto en ${formatCurrency(Math.abs(itinerary.budget_difference))}`
                : `Dentro del presupuesto (${formatCurrency(Math.abs(itinerary.budget_difference))} de margen)`}
            </p>
          </div>
        </header>

        <div className="scrollbar-themed min-h-0 flex-1 overflow-y-auto overflow-x-hidden px-6 py-6">
          <div className="space-y-4">
            {itinerary.days.map((day) => (
              <ItineraryDayCard key={day.day} day={day} />
            ))}
          </div>
        </div>

        <footer className="flex shrink-0 items-center justify-between gap-4 border-t border-[var(--color-border-subtle)] px-6 py-4">
          <p className="text-xs text-[var(--color-subtle-foreground)]">ID del viaje: {tripId}</p>
          <button
            type="button"
            onClick={onClose}
            className="rounded-[var(--radius-md)] border border-[var(--color-border-subtle)] px-5 py-2.5 text-sm font-medium text-[var(--color-foreground)] transition-colors hover:border-[var(--color-cream-300)]"
          >
            Cerrar
          </button>
        </footer>
      </div>
    </div>
  )
}
