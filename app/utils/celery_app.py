from celery import Celery
from app.core.config import settings


celery_app  = Celery(main='tasks', broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)
celery_app.conf.update(broker_connection_retry_on_startup=True)
celery_app.autodiscover_tasks(['app.utils.tasks'])