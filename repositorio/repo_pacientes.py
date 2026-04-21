"""
[Repository] Abstracción y operaciones de base de datos para la colección de pacientes.
"""
class RepoPacientes:
    def __init__(self, db_conexion):
        self.db = db_conexion.obtener_db()
        self.coleccion = self.db["pacientes"]

    def obtener_paciente(self, paciente_id):
        # Excluimos el _id interno de Mongo para evitar problemas de serialización
        return self.coleccion.find_one({"paciente_id": paciente_id}, {"_id": 0})

    def registrar_paciente(self, paciente_id, nombre="Paciente No Registrado"):
        """
        Upsert: Si el paciente ya existe, no hace nada; si no existe, lo crea.
        """
        nuevo_paciente = {
            "paciente_id": paciente_id,
            "nombre": nombre,
            "historial_altas": 0
        }
        
        self.coleccion.update_one(
            {"paciente_id": paciente_id},
            {"$setOnInsert": nuevo_paciente},
            upsert=True
        )
        return nuevo_paciente