from budgettrip.application.ports.notifier_port import EmailSender
from budgettrip.infrastructure.config import Settings
from budgettrip.infrastructure.notifications.email_sender import SmtpEmailSender
from budgettrip.infrastructure.notifications.null_email_sender import NullEmailSender


def build_email_sender(settings: Settings) -> EmailSender:
    if settings.smtp_host and settings.smtp_user and settings.smtp_password:
        return SmtpEmailSender(settings)
    return NullEmailSender()
