"""
[Singleton] Mantiene y provee una única instancia de conexión viva a MongoDB.
"""

from pymongo import MongoClient
import logging

class ConexionMongo:
    """
    Patrón Singleton para gestionar una única instancia de conexión a la base de datos
    durante todo el ciclo de vida del Servidor Principal.
    """
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            logging.info("Inicializando conexión Singleton a MongoDB...")
            cls._instancia = super(ConexionMongo, cls).__new__(cls)
            
            # Conexión al contenedor de Docker expuesto en localhost
            cls._instancia.cliente = MongoClient("mongodb://127.0.0.1:27017/")
            
            # Seleccionamos la base de datos del proyecto
            cls._instancia.db = cls._instancia.cliente["hospital_db"]
            
        return cls._instancia

    def obtener_db(self):
        return self.db