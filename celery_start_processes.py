from app.utils.celery_app import celery


if __name__ == "__main__":
    celery.start()
