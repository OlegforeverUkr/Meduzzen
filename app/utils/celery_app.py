from datetime import timedelta, datetime

from celery import Celery
from celery.schedules import crontab
from sqlalchemy import select

from app.core.config import settings
from app.db.connect_db import AsyncSessionFactory
from app.db.models import User, QuizResult, Quiz, Notification


celery = Celery('tasks', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)
celery.conf.update(broker_connection_retry_on_startup=True)



@celery.task
async def run_user_quiz_check():
    async with AsyncSessionFactory() as db:
        users = await db.execute(User)
        users = users.scalars().all()

        for user in users:
            quiz_results = await db.execute(select(QuizResult).where(QuizResult.user_id == user.id))
            quiz_results = quiz_results.scalars().all()

            for quiz_result in quiz_results:
                quiz = await db.get(Quiz, quiz_result.quiz_id)

                if datetime.utcnow() - quiz_result.solved_at > timedelta(days=quiz.frequency_days):
                    notification_message = f"Пора пройти квиз '{quiz.title}'!"
                    notification = Notification(user_id=user.id, message=notification_message)
                    db.add(notification)


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