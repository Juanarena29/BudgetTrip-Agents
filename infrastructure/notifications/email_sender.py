import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from budgettrip.application.ports.notifier_port import EmailSender
from budgettrip.infrastructure.config import Settings


class SmtpEmailSender(EmailSender):
    def __init__(self, settings: Settings, recipient: str | None = None) -> None:
        self._host = settings.smtp_host
        self._port = settings.smtp_port
        self._user = settings.smtp_user
        self._password = settings.smtp_password
        self._recipient = recipient or settings.smtp_user

    def send(self, subject: str, html_body: str) -> None:
        if not self._host or not self._user or not self._password:
            raise ValueError("SMTP no está configurado (SMTP_HOST, SMTP_USER, SMTP_PASSWORD)")

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self._user
        message["To"] = self._recipient
        message.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP(self._host, self._port) as server:
            server.starttls()
            server.login(self._user, self._password)
            server.sendmail(self._user, [self._recipient], message.as_string())
