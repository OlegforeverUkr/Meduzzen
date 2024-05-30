from datetime import timedelta, datetime
from celery.schedules import crontab
from sqlalchemy import select
from sqlalchemy.sql.expression import lambda_stmt
from app.db.connect_db import AsyncSessionFactory
from app.db.models import User, QuizResult, Quiz, Notification
from app.utils.send_emails import get_email_template_message
from app.utils.smtp_client import SMTPClientContext
from app.utils.celery_app import celery_app as celery


@celery.task
def send_message_to_email(user_email: str, username: str, message_text: str = None):
    if not message_text:
        message_text = get_email_template_message(username)

    with SMTPClientContext() as smtp_client:
        smtp_client.send_email(to_email=user_email, content=message_text)

    return f"Email sent to {username}"


@celery.task
async def run_user_quiz_check():
    async with AsyncSessionFactory() as session:
        users = await session.execute(select(User))
        users = users.scalars().all()

        for user in users:
            quiz_results = await session.execute(select(QuizResult).where(lambda_stmt(lambda: QuizResult.user_id == user.id)))
            quiz_results = quiz_results.scalars().all()

            for quiz_result in quiz_results:
                quiz = await session.get(Quiz, quiz_result.quiz_id)

                if datetime.utcnow() - quiz_result.solved_at > timedelta(days=quiz.frequency_days):
                    notification_message = f"It's time to take the quiz '{quiz.title}'!"
                    notification = Notification(user_id=user.id, message=notification_message)
                    session.add(notification)
                    await session.commit()

                    send_message_to_email.delay(user.email, user.username)


@celery.task
def test_task():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"The verification task was completed successfully! Current time: {current_time}"



celery.add_periodic_task(crontab(hour='0', minute='0', day_of_week='*'),
                         run_user_quiz_check.s(),
                         name='run-every-day-at-midnight')
celery.add_periodic_task(timedelta(seconds=30), test_task.s(), name='run-test-task')