import { useEffect, useRef, useState } from 'react'
import { confirmTrip, isApiConfigured, sendChatMessage } from '@/lib/api'
import type { ChatMessage, Itinerary, PlanningPhase, TripPreview } from '@/types/api'
import { AppHeader } from '@/components/AppHeader'
import { ItineraryModal } from '@/components/ItineraryModal'
import { MessageBubble } from '@/components/MessageBubble'
import { TripActionPanel } from '@/components/TripActionPanel'
import { Button } from '@/components/ui/Button'

const EXAMPLE_PROMPT =
  'Quiero un viaje a Londres ida y vuelta desde Buenos Aires, 10 días, del 1/2/27 al 11/2/27, tengo 3500 USD de presupuesto, me gusta la gastronomía, el arte y las salidas nocturnas.'

const INITIAL_ASSISTANT_MESSAGE =
  'Contame tu viaje ideal: destino, origen, fechas, presupuesto y qué te gusta hacer. Puedo ir completando los detalles con vos.'

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: INITIAL_ASSISTANT_MESSAGE },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [tripPreview, setTripPreview] = useState<TripPreview | null>(null)
  const [itinerary, setItinerary] = useState<Itinerary | null>(null)
  const [tripId, setTripId] = useState<string | null>(null)
  const [phase, setPhase] = useState<PlanningPhase>('chatting')
  const [itineraryModalOpen, setItineraryModalOpen] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const chatEnabled = phase === 'chatting' && !loading && !confirming

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading, confirming, phase])

  useEffect(() => {
    if (chatEnabled) {
      textareaRef.current?.focus()
    }
  }, [chatEnabled])

  async function handleSend(messageText?: string) {
    const trimmed = (messageText ?? input).trim()
    if (!trimmed || !chatEnabled) return

    if (!isApiConfigured()) {
      setError('Configurá VITE_API_KEY en frontend/.env (mismo valor que API_SECRET_KEY del backend).')
      return
    }

    setError(null)
    setInput('')
    setLoading(true)

    const userMessage: ChatMessage = { role: 'user', content: trimmed }
    const history = messages.filter((message) => message.content !== INITIAL_ASSISTANT_MESSAGE)
    setMessages((current) => [...current, userMessage])

    try {
      const response = await sendChatMessage(trimmed, history, sessionId ?? undefined)
      if (response.session_id) {
        setSessionId(response.session_id)
      }
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.assistant_message,
      }
      setMessages((current) => [...current, assistantMessage])

      if (response.complete && response.trip) {
        setTripPreview(response.trip)
        setPhase('review')
      } else {
        setTripPreview(null)
        setPhase('chatting')
      }
    } catch (sendError) {
      setError(sendError instanceof Error ? sendError.message : 'No se pudo enviar el mensaje.')
    } finally {
      setLoading(false)
      if (chatEnabled) {
        textareaRef.current?.focus()
      }
    }
  }

  async function handleConfirm() {
    if (!tripPreview || confirming || phase !== 'review') return

    setConfirming(true)
    setPhase('planning')
    setError(null)

    try {
      const result = await confirmTrip(tripPreview)
      setItinerary(result.itinerary)
      setTripId(result.id)
      setPhase('done')
      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content:
            'Listo. Tu itinerario fue generado. Usá el botón "Ver itinerario" en el panel para explorarlo.',
        },
      ])
    } catch (confirmError) {
      setPhase('review')
      setError(confirmError instanceof Error ? confirmError.message : 'No se pudo planificar el viaje.')
    } finally {
      setConfirming(false)
    }
  }

  function handleModify() {
    if (phase !== 'review') return

    setPhase('chatting')
    setTripPreview(null)
    setError(null)
    setMessages((current) => [
      ...current,
      {
        role: 'assistant',
        content: 'Sin problema. Contame qué querés cambiar y actualizo tu viaje.',
      },
    ])
    textareaRef.current?.focus()
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      void handleSend()
    }
  }

  const showActionPanel = tripPreview && (phase === 'review' || phase === 'planning' || phase === 'done')

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-[var(--chat-bg)]">
      <AppHeader />

      <main className="mx-auto flex min-h-0 w-full max-w-6xl flex-1 flex-col px-4 pb-4 pt-4 sm:px-6">
        <div className="mb-4 shrink-0">
          <h1 className="font-[family-name:var(--font-display)] text-2xl font-semibold sm:text-3xl">
            Planificá tu viaje
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-[var(--color-muted-foreground)]">
            Nuestros agentes entenderán tus requisitos y planificarán el viaje.
          </p>
        </div>

        <div className="grid min-h-0 flex-1 gap-4 lg:grid-cols-[minmax(0,1fr)_22rem]">
          <section className="flex min-h-0 flex-col overflow-hidden rounded-[var(--radius-xl)] border border-[var(--card-border)] bg-[var(--chat-surface)] shadow-[var(--shadow-soft)]">
            <div className="scrollbar-themed min-h-0 flex-1 space-y-4 overflow-y-auto px-4 py-5 sm:px-6">
              {messages.map((message, index) => (
                <MessageBubble
                  key={`${message.role}-${index}-${message.content.slice(0, 24)}`}
                  role={message.role}
                  content={message.content}
                />
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="rounded-[var(--radius-lg)] border border-[var(--card-border)] bg-[var(--chat-assistant-bubble)] px-4 py-3">
                    <div className="flex items-center gap-2 text-sm text-[var(--color-muted-foreground)]">
                      <span className="h-2 w-2 animate-pulse rounded-full bg-[var(--color-cream-300)]" />
                      <span className="h-2 w-2 animate-pulse rounded-full bg-[var(--color-cream-300)] [animation-delay:150ms]" />
                      <span className="h-2 w-2 animate-pulse rounded-full bg-[var(--color-cream-300)] [animation-delay:300ms]" />
                      Procesando...
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {error && (
              <div className="mx-4 mb-3 shrink-0 rounded-[var(--radius-md)] border border-[var(--color-warning)]/40 bg-[var(--color-wine-800)]/40 px-4 py-3 text-sm text-[var(--color-cream-100)] sm:mx-6">
                {error}
              </div>
            )}

            <div className="shrink-0 border-t border-[var(--color-border-subtle)] p-4 sm:p-5">
              {phase === 'review' && (
                <p className="mb-3 rounded-[var(--radius-md)] border border-[var(--color-border-subtle)] bg-[var(--color-surface-elevated)] px-4 py-3 text-sm text-[var(--color-muted-foreground)]">
                  Requisitos completos. Usá <strong className="text-[var(--color-foreground)]">Confirmar y planificar</strong>{' '}
                  o <strong className="text-[var(--color-foreground)]">Modificar</strong> en el panel lateral.
                </p>
              )}

              {phase === 'planning' && (
                <p className="mb-3 rounded-[var(--radius-md)] border border-[var(--color-border-subtle)] bg-[var(--color-surface-elevated)] px-4 py-3 text-sm text-[var(--color-muted-foreground)]">
                  Planificando tu viaje. El chat permanece bloqueado mientras los agentes trabajan.
                </p>
              )}

              {phase === 'done' && (
                <p className="mb-3 rounded-[var(--radius-md)] border border-[var(--color-border-subtle)] bg-[var(--color-surface-elevated)] px-4 py-3 text-sm text-[var(--color-muted-foreground)]">
                  Itinerario generado. Abrilo con el botón <strong className="text-[var(--color-foreground)]">Ver itinerario</strong>.
                </p>
              )}

              {chatEnabled && messages.length <= 1 && (
                <button
                  type="button"
                  onClick={() => void handleSend(EXAMPLE_PROMPT)}
                  className="mb-3 w-full rounded-[var(--radius-lg)] border border-dashed border-[var(--color-border-subtle)] px-4 py-3 text-left text-sm text-[var(--color-muted-foreground)] transition-colors hover:border-[var(--color-cream-300)] hover:text-[var(--color-foreground)]"
                >
                  Probar con un ejemplo →
                </button>
              )}

              <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
                <textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  onKeyDown={handleKeyDown}
                  rows={3}
                  disabled={!chatEnabled}
                  placeholder={
                    chatEnabled
                      ? 'Describí tu viaje: origen, destino, fechas, presupuesto, intereses...'
                      : 'Chat bloqueado — usá los botones del panel lateral'
                  }
                  className="min-h-[5.5rem] flex-1 resize-none rounded-[var(--radius-lg)] border border-[var(--chat-input-border)] bg-[var(--chat-input-bg)] px-4 py-3 text-sm text-[var(--color-foreground)] placeholder:text-[var(--color-subtle-foreground)] disabled:cursor-not-allowed disabled:opacity-50"
                />
                <Button
                  onClick={() => void handleSend()}
                  loading={loading}
                  disabled={!chatEnabled || !input.trim()}
                  className="w-full sm:w-auto sm:min-w-[7.5rem]"
                >
                  Enviar
                </Button>
              </div>
            </div>
          </section>

          <aside className="scrollbar-themed flex min-h-0 flex-col gap-4 overflow-y-auto lg:overflow-visible">
            {showActionPanel && tripPreview && (
              <TripActionPanel
                trip={tripPreview}
                phase={phase}
                confirming={confirming}
                onConfirm={() => void handleConfirm()}
                onModify={handleModify}
                onViewItinerary={() => setItineraryModalOpen(true)}
              />
            )}
          </aside>
        </div>
      </main>

      {itinerary && tripId && (
        <ItineraryModal
          itinerary={itinerary}
          tripId={tripId}
          open={itineraryModalOpen}
          onClose={() => setItineraryModalOpen(false)}
        />
      )}
    </div>
  )
}
