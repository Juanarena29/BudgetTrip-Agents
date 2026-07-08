export type ChatRole = 'user' | 'assistant'

export interface ChatMessage {
  role: ChatRole
  content: string
}

export interface TripPreview {
  origin: string
  destination: string
  start_date: string
  end_date: string
  budget_limit: number
  preferences: string[]
}

export interface ChatResponse {
  session_id: string
  assistant_message: string
  complete: boolean
  missing_fields: string[]
  trip: TripPreview | null
}

export interface CostItem {
  day: number
  category: string
  description: string
  estimated_cost: number
}

export interface DayPlan {
  day: number
  date: string
  summary: string
  activities: string[]
  cost_items: CostItem[]
  day_total: number
}

export interface Itinerary {
  destination: string
  days: DayPlan[]
  total_cost: number
  over_budget: boolean
  budget_difference: number
  short_summary: string
}

export interface TripCreatedResponse {
  id: string
  itinerary: Itinerary
}

export type PlanningPhase = 'chatting' | 'review' | 'planning' | 'done'
