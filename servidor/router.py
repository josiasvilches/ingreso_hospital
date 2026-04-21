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
        elif dto.accion == AccionHospital.CONSULTAR_ALTAS: # NUEVA RUTA
            return self._manejar_consulta(dto)
        else:
            return {"status": "error", "mensaje": "Acción desconocida."}
    
    def _manejar_autenticacion(self, dto):
        self.pipe_auth.send(dto)
        return self.pipe_auth.recv()

    def _manejar_alta(self, dto):
        # Registramos al paciente en la base de datos de manera sincrónica
        self.repo_pacientes.registrar_paciente(dto.paciente_id)
        
        # Delegamos la carga pesada a Celery de forma asincrónica
        procesar_alta_paciente.delay(dto.paciente_id, dto.medico_id)
        return {"status": "ok", "mensaje": "Petición recibida. El código OTP se está generando en segundo plano."}
    
    def _manejar_validacion(self, dto):
        resultado = self.repo_codigos.usar_codigo(dto.codigo)
        
        if resultado:
            return {"status": "ok", "nombre": resultado.get("paciente_id"), "habitacion": "Pendiente de asignación"}
        else:
            return {"status": "error", "mensaje": "Código inválido, expirado o ya utilizado."}
    
    def _manejar_consulta(self, dto):
        codigos = self.repo_codigos.obtener_codigos_por_medico(dto.medico_id)
        return {"status": "ok", "datos": codigos}