import type { TripPreview } from '@/types/api'
import type { PlanningPhase } from '@/types/api'
import { daysBetween, formatLocalDate } from '@/lib/dates'
import { Button } from '@/components/ui/Button'

interface TripActionPanelProps {
  trip: TripPreview
  phase: PlanningPhase
  confirming: boolean
  onConfirm: () => void
  onModify: () => void
  onViewItinerary: () => void
}

function formatDate(value: string): string {
  return formatLocalDate(value, {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function tripDays(trip: TripPreview): number {
  return daysBetween(trip.start_date, trip.end_date)
}

export function TripActionPanel({
  trip,
  phase,
  confirming,
  onConfirm,
  onModify,
  onViewItinerary,
}: TripActionPanelProps) {
  const isReview = phase === 'review'
  const isPlanning = phase === 'planning'
  const isDone = phase === 'done'

  return (
    <div className="rounded-[var(--radius-xl)] border border-[var(--card-border)] bg-[var(--card-bg)] p-5 shadow-[var(--shadow-soft)]">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <p className="text-[0.6875rem] font-medium uppercase tracking-[0.14em] text-[var(--color-subtle-foreground)]">
            {isDone ? 'Viaje planificado' : 'Resumen del viaje'}
          </p>
          <h3 className="mt-1 font-[family-name:var(--font-display)] text-xl font-semibold text-[var(--color-foreground)]">
            {trip.origin} → {trip.destination}
          </h3>
        </div>
        <span className="rounded-full border border-[var(--color-border-subtle)] px-3 py-1 text-xs text-[var(--color-muted-foreground)]">
          {tripDays(trip)} días
        </span>
      </div>

      <dl className="grid gap-3 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-[var(--color-subtle-foreground)]">Fechas</dt>
          <dd className="mt-0.5 text-[var(--color-foreground)]">
            {formatDate(trip.start_date)} — {formatDate(trip.end_date)}
          </dd>
        </div>
        <div>
          <dt className="text-[var(--color-subtle-foreground)]">Presupuesto</dt>
          <dd className="mt-0.5 text-[var(--color-foreground)]">
            USD {trip.budget_limit.toLocaleString('es-AR')}
          </dd>
        </div>
      </dl>

      {trip.preferences.length > 0 && (
        <div className="mt-4">
          <p className="mb-2 text-sm text-[var(--color-subtle-foreground)]">Preferencias</p>
          <div className="flex flex-wrap gap-2">
            {trip.preferences.map((preference) => (
              <span
                key={preference}
                className="rounded-full border border-[var(--color-border-subtle)] bg-[var(--color-surface-elevated)] px-3 py-1 text-xs text-[var(--color-muted-foreground)]"
              >
                {preference}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="mt-5 border-t border-[var(--color-border-subtle)] pt-4">
        {isReview && (
          <>
            <p className="mb-3 text-sm text-[var(--color-muted-foreground)]">
              Revisá los datos. Para continuar, confirmá o modificá desde acá — el chat queda bloqueado
              hasta que elijas.
            </p>
            <div className="flex flex-col gap-2 sm:flex-row">
              <Button onClick={onConfirm} loading={confirming} className="w-full sm:flex-1">
                Confirmar y planificar
              </Button>
              <Button variant="outline" onClick={onModify} disabled={confirming} className="w-full sm:flex-1">
                Modificar
              </Button>
            </div>
          </>
        )}

        {isPlanning && (
          <div className="flex items-center gap-3 text-sm text-[var(--color-muted-foreground)]">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            Planner delegando búsquedas y Writer armando el itinerario...
          </div>
        )}

        {isDone && (
          <>
            <p className="mb-3 text-sm text-[var(--color-muted-foreground)]">
              Tu itinerario está listo. Abrilo para ver el detalle día por día.
            </p>
            <Button onClick={onViewItinerary} className="w-full tracking-[0.06em]">
              VER ITINERARIO
            </Button>
          </>
        )}
      </div>
    </div>
  )
}
