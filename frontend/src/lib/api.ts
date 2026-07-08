import type {
  ChatMessage,
  ChatResponse,
  TripCreatedResponse,
  TripPreview,
} from '@/types/api'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''
const API_KEY = import.meta.env.VITE_API_KEY ?? ''

function authHeaders(): HeadersInit {
  return {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY,
  }
}

async function parseError(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string | { msg?: string }[] }
    if (typeof data.detail === 'string') return data.detail
    if (Array.isArray(data.detail) && data.detail[0]?.msg) {
      return data.detail[0].msg
    }
  } catch {
    /* ignore */
  }
  return `Error ${response.status}: ${response.statusText}`
}

export async function sendChatMessage(
  message: string,
  history: ChatMessage[],
  sessionId?: string,
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/api/v1/chat`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ message, history, session_id: sessionId ?? null }),
  })

  if (!response.ok) {
    throw new Error(await parseError(response))
  }

  return response.json() as Promise<ChatResponse>
}

export async function confirmTrip(
  trip: TripPreview,
  sendEmail = false,
): Promise<TripCreatedResponse> {
  const response = await fetch(`${API_BASE}/api/v1/chat/confirm`, {
    method: 'POST',
    headers: authHeaders(),
    body: JSON.stringify({ trip, send_email: sendEmail }),
  })

  if (!response.ok) {
    throw new Error(await parseError(response))
  }

  return response.json() as Promise<TripCreatedResponse>
}

export function isApiConfigured(): boolean {
  return Boolean(API_KEY)
}
