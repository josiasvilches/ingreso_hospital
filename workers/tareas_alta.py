"""
[Unit of Work] Tareas que Celery procesa en background (ej. generar el código de 6 caracteres 
y coordinar el guardado con el repositorio de forma asíncrona).
"""
import time
import random
import string
import logging
import os
from pymongo import MongoClient
from celery.signals import worker_process_init
from workers.celery_app import app
from datetime import datetime, timezone

# Configuración de log local para el worker
logging.basicConfig(level=logging.INFO)
MONGO_HOST = os.environ.get('MONGO_HOST', '127.0.0.1')

# Declaramos las variables globalmente pero NO las instanciamos aquí
cliente_mongo = None
db = None
coleccion_codigos = None

@worker_process_init.connect
def inicializar_conexion_db(**kwargs):
    """
    Señal de Celery: Esta función se ejecuta automáticamente en cada proceso hijo
    ÚNICAMENTE después de que el os.fork() haya concluido.
    Garantiza que la conexión a MongoDB sea segura y aislada para cada worker.
    """
    global cliente_mongo, db, coleccion_codigos
    cliente_mongo = MongoClient(f"mongodb://{MONGO_HOST}:27017/")
    db = cliente_mongo["hospital_db"]
    coleccion_codigos = db["codigos"]
    logging.info("Conexión a MongoDB inicializada en el worker de manera fork-safe.")

def generar_string_aleatorio(longitud=6):
    letras_y_numeros = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letras_y_numeros) for i in range(longitud))

@app.task(name='workers.tareas_alta.procesar_alta_paciente')
def procesar_alta_paciente(paciente_id: str, medico_id: str):
    logging.info(f"Iniciando tarea de alta para paciente {paciente_id} (Médico: {medico_id})")
    
    # Simular un procesamiento complejo o delay de red externa
    time.sleep(4)
    
    codigo_generado = generar_string_aleatorio(6)
    
    documento = {
        "codigo": codigo_generado,
        "paciente_id": paciente_id,
        "medico_id": medico_id,
        "estado": "pendiente",
        "creado_en": datetime.now(timezone.utc) # Agregamos el timestamp exacto de creación en formato UTC para vencimiento códigos
    }
    
    coleccion_codigos.insert_one(documento)
    
    logging.info(f"Alta procesada exitosamente. Código {codigo_generado} generado y guardado en BD.")
    
    return {"status": "ok", "codigo": codigo_generado, "paciente_id": paciente_id}