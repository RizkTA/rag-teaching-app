from celery import Celery

celery_app = Celery(
    "rag_v6",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)

celery_app.conf.broker_connection_retry_on_startup = True