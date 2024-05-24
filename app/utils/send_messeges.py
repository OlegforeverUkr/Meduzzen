from email.message import EmailMessage
from app.core.config import settings


def get_email_template_message(username: str):
    email = EmailMessage()
    email['Subject'] = 'Пора заново пройки квиз!'
    email['From'] = settings.EMAIL_FROM
    email['To'] = settings.EMAIL_TO

    email.set_content(
        '<div>'
        f'<h1 style="color: red;">Здравствуйте, {username}, вы можете заново пройти квиз!.😊</h1>'
        '<img src="https://static-cse.canva.com/blob/580798/21.35d33ae2.avif" width="600">'
        '</div>',
        subtype='html'
    )
    return email