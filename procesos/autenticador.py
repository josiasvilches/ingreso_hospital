"""
Subproceso que se conecta por Pipe con el main y se dedica a validar las credenciales de los médicos.
"""
import logging
import os
from pymongo import MongoClient
from modelos import AccionHospital

def proceso_autenticador(pipe_conexion):
    """
    Subproceso aislado para validación de credenciales.
    Realiza consultas a MongoDB sin bloquear el Event Loop del servidor principal.
    """
    logging.info("Subproceso Autenticador (IPC) iniciado y esperando peticiones.")
    
    # Capturamos la variable de entorno en caso de estar en una arquitectura distribuida
    host_mongo = os.environ.get('HOSPITAL_HOST', '127.0.0.1')
    
    try:
        # 1. Instanciamos la conexión aquí adentro para garantizar el aislamiento del proceso
        cliente_mongo = MongoClient(f"mongodb://{host_mongo}:27017/")
        db = cliente_mongo["hospital_db"]
        coleccion_usuarios = db["usuarios"]
        logging.info("Conexión a base de datos de usuarios establecida con éxito.")
    except Exception as e:
        logging.error(f"Fallo crítico al conectar el Autenticador con MongoDB: {e}")
        return

    while True:
        try:
            # Revisa si hay mensajes en el Pipe sin saturar la CPU
            if pipe_conexion.poll(timeout=1.0):
                dto = pipe_conexion.recv()
                
                if dto.accion == AccionHospital.AUTENTICAR:
                    
                    # 2. Reemplazamos el diccionario en memoria por una query real a MongoDB
                    usuario_encontrado = coleccion_usuarios.find_one({
                        "usuario": dto.usuario,
                        "password": dto.password
                    })
                    
                    if usuario_encontrado:
                        respuesta = {"status": "ok", "mensaje": f"Autenticación exitosa. Bienvenido {dto.usuario}."}
                    else:
                        respuesta = {"status": "error", "mensaje": "Credenciales inválidas o usuario inexistente."}
                        
                    # Devuelve la respuesta por el túnel IPC
                    pipe_conexion.send(respuesta)
                    
        except EOFError:
            break
        except KeyboardInterrupt:
            logging.info("Apagando subproceso autenticador...")
            cliente_mongo.close()
            break