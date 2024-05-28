import smtplib
from email.message import EmailMessage
from app.core.config import settings


class SMTPClient:

    def __init__(self):
        self.server = smtplib.SMTP(host=settings.GMAIL_HOST, port=settings.GMAIL_PORT)
        self.server.starttls()
        self.server.login(user=settings.EMAIL_FROM, password=settings.EMAIL_PASSWORD)


    def send_email(self, to_email: str, content: str):
        message = EmailMessage()
        message['Subject'] = 'Message from company admin'
        message['From'] = settings.EMAIL_FROM
        message['To'] = to_email
        message.set_content(content)
        self.server.send_message(from_addr=settings.EMAIL_FROM, to_addrs=to_email, msg=message)


    def close(self):
        self.server.quit()


class SMTPClientContext:
    def __enter__(self):
        self.client = SMTPClient()
        return self.client


    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()
