from celery import Celery
from datetime import timedelta, datetime
from sqlalchemy import select

from app.core.config import settings
from app.db.connect_db import AsyncSessionFactory
from app.db.models import User, QuizResult, Quiz, Notification


celery = Celery('tasks', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)


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
    print(f"Проверочная задача выполнена успешно! Текущее время: {current_time}")


celery.conf.beat_schedule = {
    'run-every-day-at-midnight': {
        'task': 'tasks.run_user_quiz_check',
        'schedule': timedelta(days=1),
    },
    'run-test-task': {
        'task': 'tasks.test_task',
        'schedule': timedelta(seconds=30),
    }
}