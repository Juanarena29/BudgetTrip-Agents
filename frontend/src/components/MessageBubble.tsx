import type { ChatRole } from '@/types/api'

interface MessageBubbleProps {
  role: ChatRole
  content: string
}

export function MessageBubble({ role, content }: MessageBubbleProps) {
  const isUser = role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[min(100%,42rem)] rounded-[var(--radius-lg)] px-4 py-3 text-[0.9375rem] leading-relaxed ${
          isUser
            ? 'bg-[var(--chat-user-bubble)] text-[var(--color-cream-50)] shadow-[var(--shadow-glow)]'
            : 'border border-[var(--card-border)] bg-[var(--chat-assistant-bubble)] text-[var(--color-foreground)]'
        }`}
      >
        {!isUser && (
          <p className="mb-1.5 text-[0.6875rem] font-medium uppercase tracking-[0.12em] text-[var(--color-subtle-foreground)]">
            Agente de requisitos
          </p>
        )}
        <p className="whitespace-pre-wrap">{content}</p>
      </div>
    </div>
  )
}
