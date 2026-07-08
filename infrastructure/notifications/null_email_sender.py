from budgettrip.application.ports.notifier_port import EmailSender


class NullEmailSender(EmailSender):
    def send(self, subject: str, html_body: str) -> None:
        pass
