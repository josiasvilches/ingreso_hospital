"""
[Chain of Responsibility] Recibe los DTOs desde la conexión TCP y
los deriva al servicio o función encargada de procesarlos.
"""
import logging
from modelos import AccionHospital
from workers.tareas_alta import procesar_alta_paciente
from repositorio.repo_codigos import RepoCodigos
from repositorio.repo_pacientes import RepoPacientes
from servidor.middleware import logging_y_auditoria
from datetime import datetime, timezone

TIEMPO_EXPIRACION_SEGUNDOS = 30 # tiempo de validez códigos, 30 seg para muestras, debería durar 15 minutos

class RouterDTO:
    def __init__(self, db_conexion, pipe_auth_envio):
        self.db_conexion = db_conexion
        self.pipe_auth = pipe_auth_envio
        # Inyección de dependencias de la capa de persistencia
        self.repo_codigos = RepoCodigos(self.db_conexion)
        self.repo_pacientes = RepoPacientes(self.db_conexion)

    @logging_y_auditoria
    def enrutar(self, dto):
        if dto.accion == AccionHospital.AUTENTICAR:
            return self._manejar_autenticacion(dto)
        elif dto.accion == AccionHospital.ALTA:
            return self._manejar_alta(dto)
        elif dto.accion == AccionHospital.VALIDAR:
            return self._manejar_validacion(dto)
        else:
            return {"status": "error", "mensaje": "Acción desconocida."}
    
    def _manejar_autenticacion(self, dto):
        self.pipe_auth.send(dto)
        return self.pipe_auth.recv()

    def _manejar_alta(self, dto):
        # Registramos al paciente en la base de datos
        self.repo_pacientes.registrar_paciente(dto.paciente_id)
        
        # 1. Lanzamos la tarea a Celery y guardamos la referencia de la tarea
        tarea = procesar_alta_paciente.delay(dto.paciente_id, dto.medico_id)
        
        try:
            # 2. Patrón RPC: Esperamos el resultado de Celery (bloquea este hilo ~4 segs)
            # Retorna exactamente el diccionario que devuelve la tarea en tareas_alta.py
            resultado = tarea.get(timeout=10) 
            
            codigo_generado = resultado.get("codigo")
            
            return {
                "status": "ok", 
                "mensaje": f"Alta procesada con éxito. Entregue este código al paciente: [{codigo_generado}]"
            }
        except Exception as e:
            return {
                "status": "error", 
                "mensaje": f"Error al generar el código OTP: {str(e)}"
            }
    
    def _manejar_validacion(self, dto):
        # 1. Pedimos al repositorio que busque el documento sin alterarlo
        doc = self.repo_codigos.buscar_codigo_pendiente(dto.codigo)
        
        if not doc:
            return {"status": "error", "mensaje": "Código inválido, inexistente o ya utilizado."}
            
        # 2. Calculamos el tiempo transcurrido
        ahora = datetime.now(timezone.utc)
        hora_creacion = doc["creado_en"].replace(tzinfo=timezone.utc)
        segundos_transcurridos = (ahora - hora_creacion).total_seconds()
        
        # 3. Verificamos si expiró
        if segundos_transcurridos > TIEMPO_EXPIRACION_SEGUNDOS:
            # Delegamos al repositorio la actualización del estado
            self.repo_codigos.marcar_como_expirado(doc["_id"])
            segundos_pasados = int(segundos_transcurridos - TIEMPO_EXPIRACION_SEGUNDOS)
            return {
                "status": "error", 
                "mensaje": f"Acceso denegado: El código expiró hace {segundos_pasados} segundos."
            }
            
        # 4. Si es válido y está en tiempo, delegamos al repo para quemarlo
        self.repo_codigos.marcar_como_utilizado(doc["_id"])
        
        return {
            "status": "ok", 
            "nombre": doc.get("paciente_id"), 
            "habitacion": "Pendiente de asignación"
        }
    
    def _manejar_consulta(self, dto):
        codigos = self.repo_codigos.obtener_codigos_por_medico(dto.medico_id)
        return {"status": "ok", "datos": codigos}