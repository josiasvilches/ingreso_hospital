"""
Configuración e inicialización de la instancia de Celery usando Redis como broker.
"""
from celery import Celery

# Configuramos Celery para que use el Redis local en el puerto 6380 como broker
app = Celery(
    'hospital_workers',
    broker='redis://127.0.0.1:6380/0',
    backend='redis://127.0.0.1:6380/0',
    include=['workers.tareas_alta']
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Argentina/Mendoza',
    enable_utc=True,
)