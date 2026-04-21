"""
Subproceso que se conecta por Pipe con el main y se dedica a validar las credenciales de los médicos.
"""
import logging
from modelos import AccionHospital

def proceso_autenticador(pipe_conexion):
    """
    Subproceso aislado para validación de credenciales.
    Simula una carga pesada (ej. consulta a un Active Directory o LDAP)
    sin bloquear el Event Loop del servidor principal.
    """
    logging.info("Subproceso Autenticador (IPC) iniciado y esperando peticiones.")
    
    # Base de datos simulada en memoria
    medicos_autorizados = {"medico1": "1234", "admin": "admin"}
    
    while True:
        try:
            # Revisa si hay mensajes en el Pipe sin saturar la CPU
            if pipe_conexion.poll(timeout=1.0):
                dto = pipe_conexion.recv()
                
                if dto.accion == AccionHospital.AUTENTICAR:
                    if medicos_autorizados.get(dto.usuario) == dto.password:
                        respuesta = {"status": "ok", "mensaje": f"Autenticación exitosa. Bienvenido {dto.usuario}."}
                    else:
                        respuesta = {"status": "error", "mensaje": "Credenciales inválidas."}
                        
                    # Devuelve la respuesta por el túnel
                    pipe_conexion.send(respuesta)
        except EOFError:
            break
        except KeyboardInterrupt:
            break