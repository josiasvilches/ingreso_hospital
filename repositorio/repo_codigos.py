"""
[Repository] Abstracción y operaciones atómicas para los códigos de acceso 
(ej. find_one_and_update al validar entrada en garita).
"""
class RepoCodigos:
    def __init__(self, db_conexion):
        self.db = db_conexion.obtener_db()
        self.coleccion = self.db["codigos"]

    def buscar_codigo_pendiente(self, codigo):
        """Busca un código en estado pendiente y retorna el documento completo."""
        return self.coleccion.find_one({
            "codigo": codigo, 
            "estado": "pendiente"
        })

    def marcar_como_utilizado(self, doc_id):
        """Actualiza el estado del código a utilizado (quemado)."""
        self.coleccion.update_one(
            {"_id": doc_id}, 
            {"$set": {"estado": "utilizado"}}
        )

    def marcar_como_expirado(self, doc_id):
        """Actualiza el estado del código a expirado."""
        self.coleccion.update_one(
            {"_id": doc_id}, 
            {"$set": {"estado": "expirado"}}
        )

    def obtener_codigos_por_medico(self, medico_id):
        """
        Retorna todos los códigos generados por un médico específico.
        """
        cursor = self.coleccion.find({"medico_id": medico_id}, {"_id": 0})
        return list(cursor)