"""
[Repository] Abstracción y operaciones atómicas para los códigos de acceso 
(ej. find_one_and_update al validar entrada en garita).
"""
class RepoCodigos:
    def __init__(self, db_conexion):
        self.db = db_conexion.obtener_db()
        self.coleccion = self.db["codigos"]

    def usar_codigo(self, codigo_str):
        """
        Operación Atómica: Busca y actualiza en una sola transacción.
        """
        return self.coleccion.find_one_and_update(
            {"codigo": codigo_str, "estado": "pendiente"},
            {"$set": {"estado": "usado"}}
        )

    def obtener_codigos_por_medico(self, medico_id):
        """
        Retorna todos los códigos generados por un médico específico.
        """
        cursor = self.coleccion.find({"medico_id": medico_id}, {"_id": 0})
        return list(cursor)