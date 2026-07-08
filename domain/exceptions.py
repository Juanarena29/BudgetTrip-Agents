class BudgetTripError(Exception):
    """Base exception for BudgetTrip domain errors."""


class BudgetExceededError(BudgetTripError):
    """Raised when an itinerary exceeds the budget limit."""


class MaxRetriesReachedError(BudgetTripError):
    """Raised when budget adjustment retries are exhausted."""


class PlanningError(BudgetTripError):
    """Raised when trip planning fails."""
