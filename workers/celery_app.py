"""
Configuración e inicialización de la instancia de Celery usando Redis como broker.
"""
import os
from celery import Celery

# Capturamos Host y Puerto dinámicamente. 
# Si no hay variables (ej: corrés a mano), asume localhost y 6380.
REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.environ.get('REDIS_PORT', '6380')

app = Celery(
    'hospital_workers',
    broker=f'redis://{REDIS_HOST}:{REDIS_PORT}/0',
    backend=f'redis://{REDIS_HOST}:{REDIS_PORT}/0',
    include=['workers.tareas_alta']
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Argentina/Mendoza',
    enable_utc=True,
)