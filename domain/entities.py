from datetime import date as Date
from typing import Annotated

from pydantic import BaseModel, Field


class TripRequest(BaseModel):
    origin: str
    destination: str
    start_date: Date
    end_date: Date
    budget_limit: float = Field(gt=0)
    preferences: list[str] = Field(default_factory=list)


class RequirementsTurn(BaseModel):
    """Respuesta estructurada del agente de requisitos en cada turno de chat."""

    complete: bool = Field(
        description=(
            "True solo cuando origin, destination, start_date, end_date, budget_limit "
            "estén definidos y preferences_asked sea true."
        ),
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description=(
            "Nombres de campos obligatorios que aún faltan "
            "(ej. ['origin', 'budget_limit']). Debe ser [] si complete=true."
            "Conservá el valor si ya fue mencionado en la conversación"
        ),
    )
    assistant_message: str = Field(
        description=(
            "Mensaje en español que ve el usuario en el chat. "
            "Si complete=false: una sola pregunta por el campo faltante más importante. "
            "Si complete=true: breve resumen del viaje pidiendo confirmación para planificar."
            "Conservá el valor si ya fue mencionado en la conversación"
        ),
    )
    origin: str | None = Field(
        default=None,
        description="Ciudad o país de salida del viajero. None si aún no se mencionó."
            "Conservá el valor si ya fue mencionado en la conversación",
    )
    destination: str | None = Field(
        default=None,
        description="Destino del viaje. None si aún no se mencionó."
            "Conservá el valor si ya fue mencionado en la conversación",
    )
    start_date: Date | None = Field(
        default=None,
        description="Conservá el valor si ya fue mencionado en la conversación",
    )
    end_date: Date | None = Field(
        default=None,
        description="Conservá el valor si ya fue mencionado en la conversación",
    )
    budget_limit: float | None = Field(
        default=None,
        description="Presupuesto total en USD. None si aún no se mencionó."
            "Conservá el valor si ya fue mencionado en la conversación",
        gt=0,
    )
    preferences: list[str] = Field(
        default_factory=list,
        description="Gustos o restricciones opcionales (ej. gastronomía, museos, viajar con niños)."
            "Conservá el valor si ya fue mencionado en la conversación",
    )
    preferences_asked: bool = Field(
        default=False,
        description=(
            "True cuando ya preguntaste por preferencias y el usuario respondió "
            "(aunque haya dicho que no tiene)."
            "Conservá el valor si ya fue mencionado en la conversación"
        ),
    )

    def to_trip_request(self) -> TripRequest | None:
        if not self.complete or not self.preferences_asked:
            return None
        if not all(
            [
                self.origin,
                self.destination,
                self.start_date,
                self.end_date,
                self.budget_limit is not None,
            ]
        ):
            return None
        return TripRequest(
            origin=self.origin,
            destination=self.destination,
            start_date=self.start_date,
            end_date=self.end_date,
            budget_limit=self.budget_limit,
            preferences=self.preferences,
        )


class SearchItem(BaseModel):
    category: str = Field(
        description=(
            "Tipo de búsqueda asignada por el pllan"))   
    reason: str = Field(
        description=(
            "Por qué esta búsqueda importa para este viaje concreto "))
    query: str = Field(
        description=(
            "Consulta concreta para web search. Incluir destino, fechas y contexto de presupuesto "))


class SearchPlan(BaseModel):
    searches: list[SearchItem] = Field(
        description=(
            "Plan de búsquedas web a ejecutar. Debe tener exactamente la cantidad pedida "
            "en el input, con categorías variadas y sin duplicar el mismo objetivo."
        ),
    )


class CostItem(BaseModel):
    day: int = Field(
        description="Número de día del viaje (1 = primer día). Debe coincidir con el DayPlan padre.",
        ge=1,
    )
    category: str = Field(
        description=(
            "Rubro del gasto (ej. vuelo, alojamiento, comida, actividad, transporte, entrada, otro)."
        ),
        min_length=1,
    )
    description: Annotated[
        str,
        Field(
            description="Descripción breve del gasto (qué es y, si aplica, dónde o cuándo).",
            min_length=1,
        ),
    ]
    estimated_cost: float = Field(
        description="Costo estimado en USD para este ítem.",
        ge=0,
    )


class DayPlan(BaseModel):
    day: int = Field(
        description="Número secuencial del día (1 = fecha de inicio del viaje).",
        ge=1,
    )
    date: Annotated[
        Date,
        Field(
            description="Fecha real del día en formato YYYY-MM-DD, calculada desde start_date del viaje.",
        ),
    ]
    summary: str = Field(
        description="Resumen breve de qué se hace ese día.",
        min_length=1,
    )
    activities: list[str] = Field(
        description="Lista ordenada de actividades planificadas para el día.",
        min_length=1,
    )
    cost_items: list[CostItem] = Field(
        description="Gastos estimados del día. Cada item.day debe coincidir con este day.",
        min_length=1,
    )
    day_total: float = Field(
        description="Suma estimada de cost_items del día en USD. El sistema puede recalcularla."
        "Para el primer y el ultimo dia, debe haber al menos un cost_item. correspondiente a vuelo/transporte."
        "Para los dias que correspondan deben haber al menos un cost_item. correspondiente a alojamiento (y el resto de cosas segun correspondan)",
        ge=0,
    )


class Itinerary(BaseModel):
    destination: str = Field(
        description="Destino del viaje. Debe coincidir con el destino indicado en el input.",
        min_length=1,
    )
    days: list[DayPlan] = Field(
        description="Un DayPlan por cada día del viaje, en orden cronológico.",
        min_length=1,
    )
    total_cost: float = Field(
        description="Suma estimada de todos los day_total en USD. El sistema puede recalcularla.",
        ge=0,
    )
    over_budget: bool = Field(
        description="True si total_cost supera el presupuesto del viaje. El sistema puede recalcularlo.",
    )
    budget_difference: float = Field(
        description=(
            "Diferencia total_cost - presupuesto en USD. Positivo si excede; "
            "negativo o cero si está dentro. El sistema puede recalcularla."
        ),
    )
    short_summary: str = Field(
        description="Párrafo breve que resume el viaje completo para el usuario.",
        min_length=1,
    )
