import smtplib
from datetime import timedelta, datetime
from email.message import EmailMessage

from celery import Celery
from celery.schedules import crontab
from sqlalchemy import select

from app.core.config import settings
from app.db.connect_db import AsyncSessionFactory
from app.db.models import User, QuizResult, Quiz, Notification
from app.utils.send_messeges import get_email_template_message


celery = Celery('tasks', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)
celery.conf.update(broker_connection_retry_on_startup=True)


@celery.task
def send_message_to_email(user_email: str, username: str, message_text: str = None):
    if not message_text:
        message = get_email_template_message(username)
    else:
        message = EmailMessage()
        message['Subject'] = 'Message from company admin'
        message['From'] = settings.EMAIL_FROM
        message['To'] = user_email
        message.set_content(message_text)

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as server:
        server.starttls()
        server.login(user=settings.EMAIL_FROM, password=settings.EMAIL_PASSWORD)
        server.send_message(from_addr=settings.EMAIL_FROM, to_addrs=message['To'], msg=message)
    return f"Email был отправлен {username}"


@celery.task
async def run_user_quiz_check():
    async with AsyncSessionFactory() as session:
        users = await session.execute(User)
        users = users.scalars().all()

        for user in users:
            quiz_results = await session.execute(select(QuizResult).where(QuizResult.user_id == user.id))
            quiz_results = quiz_results.scalars().all()

            for quiz_result in quiz_results:
                quiz = await session.get(Quiz, quiz_result.quiz_id)

                if datetime.utcnow() - quiz_result.solved_at > timedelta(days=quiz.frequency_days):
                    notification_message = f"Пора пройти квиз '{quiz.title}'!"
                    notification = Notification(user_id=user.id, message=notification_message)
                    session.add(notification)
                    await session.commit()

                    send_message_to_email.delay(user.email, user.username)


@celery.task
def test_task():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Проверочная задача выполнена успешно! Текущее время: {current_time}"




celery.add_periodic_task(crontab(hour='0', minute='0', day_of_week='*'),
                         run_user_quiz_check.s(),
                         name='run-every-day-at-midnight')
celery.add_periodic_task(timedelta(seconds=30), test_task.s(), name='run-test-task')


# Another option for adding tasks frequency

# celery.conf.beat_schedule = {
#     'run-every-day-at-midnight': {
#         'task': 'app.celery_workflow.tasks.run_user_quiz_check',
#         'schedule': crontab(hour='0', minute='0', day_of_week='*'),
#     },
#     'run-test-task': {
#         'task': 'app.celery_workflow.tasks.test_task',
#         'schedule': timedelta(seconds=30),
#     }
# }