"""
[Middleware] Interceptores para registrar logs, manejar errores o validaciones previas.
"""
import logging
import time
from functools import wraps

def logging_y_auditoria(func):
    """
    Middleware interceptor.
    Envuelve la ejecución de las rutas para medir rendimiento 
    y dejar un rastro de auditoría sin ensuciar la lógica de negocio.
    """
    @wraps(func)
    def wrapper(self, dto, *args, **kwargs):
        inicio_tiempo = time.time()
        logging.info(f"[Middleware] Petición interceptada -> Acción: {dto.accion.value} | Origen: {dto.origen.value}")
        
        # Se ejecuta la lógica real del enrutador
        resultado_respuesta = func(self, dto, *args, **kwargs)
        
        tiempo_total = (time.time() - inicio_tiempo) * 1000
        estado = resultado_respuesta.get("status", "desconocido")
        
        logging.info(f"[Middleware] Procesamiento finalizado en {tiempo_total:.2f}ms | Estado final: {estado.upper()}")
        
        return resultado_respuesta
    return wrapper