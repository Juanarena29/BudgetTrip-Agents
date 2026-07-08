from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from budgettrip.domain.entities import CostItem, DayPlan, Itinerary
from budgettrip.infrastructure.config import Settings
from budgettrip.infrastructure.notifications.email_sender import SmtpEmailSender
from budgettrip.infrastructure.notifications.ics_exporter import IcsExporter
from budgettrip.infrastructure.notifications import build_email_sender
from budgettrip.infrastructure.notifications.null_email_sender import NullEmailSender


@pytest.fixture
def smtp_settings() -> Settings:
    return Settings(
        openai_api_key="",
        api_secret_key="",
        allowed_origins=[],
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_user="user@example.com",
        smtp_password="secret",
        how_many_searches=8,
        model_name="gpt-5.4-mini",
    )


def _sample_itinerary() -> Itinerary:
    return Itinerary(
        destination="Barcelona",
        days=[
            DayPlan(
                day=1,
                date=date(2026, 8, 1),
                summary="Gótico y Ramblas",
                activities=["Catedral", "Paseo por Las Ramblas"],
                cost_items=[
                    CostItem(
                        day=1,
                        category="activity",
                        description="Entrada catedral",
                        estimated_cost=15.0,
                    )
                ],
                day_total=15.0,
            ),
            DayPlan(
                day=2,
                date=date(2026, 8, 2),
                summary="Gaudí",
                activities=["Sagrada Familia"],
                cost_items=[
                    CostItem(
                        day=2,
                        category="activity",
                        description="Ticket Sagrada Familia",
                        estimated_cost=30.0,
                    )
                ],
                day_total=30.0,
            ),
        ],
        total_cost=45.0,
        over_budget=False,
        budget_difference=-1155.0,
        short_summary="Fin de semana en Barcelona",
    )


def test_build_email_sender_uses_smtp_when_configured(smtp_settings: Settings):
    sender = build_email_sender(smtp_settings)
    assert isinstance(sender, SmtpEmailSender)


def test_build_email_sender_falls_back_to_null():
    settings = Settings(
        openai_api_key="",
        api_secret_key="",
        allowed_origins=[],
        smtp_host="",
        smtp_port=587,
        smtp_user="",
        smtp_password="",
        how_many_searches=8,
        model_name="gpt-5.4-mini",
    )
    sender = build_email_sender(settings)
    assert isinstance(sender, NullEmailSender)


@patch("budgettrip.infrastructure.notifications.email_sender.smtplib.SMTP")
def test_smtp_email_sender_sends_html(mock_smtp_class: MagicMock, smtp_settings: Settings):
    mock_server = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_server

    sender = SmtpEmailSender(smtp_settings)
    sender.send(subject="Itinerario: Barcelona", html_body="<p>Hola</p>")

    mock_smtp_class.assert_called_once_with("smtp.example.com", 587)
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("user@example.com", "secret")
    mock_server.sendmail.assert_called_once()
    _, recipients, raw_message = mock_server.sendmail.call_args.args
    assert recipients == ["user@example.com"]
    assert "Itinerario: Barcelona" in raw_message
    assert "Content-Type: text/html" in raw_message
    assert "SG9sYTwvcD4=" in raw_message


def test_smtp_email_sender_requires_configuration():
    settings = Settings(
        openai_api_key="",
        api_secret_key="",
        allowed_origins=[],
        smtp_host="",
        smtp_port=587,
        smtp_user="",
        smtp_password="",
        how_many_searches=8,
        model_name="gpt-5.4-mini",
    )
    sender = SmtpEmailSender(settings)

    with pytest.raises(ValueError, match="SMTP no está configurado"):
        sender.send(subject="Test", html_body="<p>x</p>")


def test_ics_exporter_generates_valid_calendar():
    itinerary = _sample_itinerary()
    exporter = IcsExporter()

    ics_bytes = exporter.export(itinerary)
    content = ics_bytes.decode("utf-8")

    assert content.startswith("BEGIN:VCALENDAR")
    assert "END:VCALENDAR" in content
    assert "Barcelona — Día 1" in content
    assert "Barcelona — Día 2" in content
    assert "20260801" in content
    assert "20260802" in content


def test_ics_exporter_uses_iso_dates_from_day_plan():
    itinerary = _sample_itinerary()
    content = IcsExporter().export(itinerary).decode("utf-8")

    for day in itinerary.days:
        assert day.date.strftime("%Y%m%d") in content
