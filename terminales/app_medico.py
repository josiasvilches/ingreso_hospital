"""
Interfaz de consola simulada para el médico. 
Captura datos del paciente, los empaqueta en DTOs y los envía al servidor vía TCP.
"""

import socket
import pickle
import sys
import os

# Agregamos la ruta raíz para poder importar los modelos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modelos import PeticionAutenticacionDTO, PeticionAltaDTO, PeticionConsultaDTO, AccionHospital, OrigenPeticion

HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8888

def enviar_peticion(dto):
    """
    Se conecta al servidor resolviendo dinámicamente si es IPv4 o IPv6,
    envía el objeto DTO y retorna la respuesta.
    """
    try:
        # getaddrinfo resuelve la IP ingresada y devuelve la familia correcta (AF_INET o AF_INET6)
        direcciones = socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as e:
        print(f"[Error de Red] No se pudo resolver la dirección {HOST}: {e}")
        return None

    conexion = None
    # Iteramos sobre las resoluciones posibles hasta que una conecte
    for familia, tipo_socket, protocolo, _, direccion_socket in direcciones:
        try:
            conexion = socket.socket(familia, tipo_socket, protocolo)
            conexion.settimeout(5.0)  # Evita que el cliente se cuelgue infinito si el servidor no responde
            conexion.connect(direccion_socket)
            break  # Conexión exitosa, salimos del bucle
        except OSError:
            if conexion:
                conexion.close()
            conexion = None
            
    if conexion is None:
        print(f"[Error de Red] No se pudo conectar al servidor en {HOST}:{PORT}")
        return None

    try:
        # Serializar y enviar
        conexion.send(pickle.dumps(dto))
        # Esperar y deserializar respuesta
        respuesta_bytes = conexion.recv(4096)
        if not respuesta_bytes:
            return None
        return pickle.loads(respuesta_bytes)
    except Exception as e:
        print(f"[Error de Comunicación] Hubo un fallo en la transferencia: {e}")
        return None
    finally:
        conexion.close()

def main():
    print("=== TERMINAL MÉDICO ===")
    autenticado = False
    medico_id = ""

    # Bucle 1: Autenticación
    while not autenticado:
        print("\n--- Iniciar Sesión ---")
        usuario = input("Ingrese su usuario: ")
        password = input("Ingrese su contraseña: ")

        peticion_auth = PeticionAutenticacionDTO(
            accion=AccionHospital.AUTENTICAR,
            origen=OrigenPeticion.MEDICO,
            usuario=usuario,
            password=password
        )

        respuesta = enviar_peticion(peticion_auth)
        
        if respuesta and respuesta.get("status") == "ok":
            print(f"[Sistema] {respuesta.get('mensaje')}")
            autenticado = True
            medico_id = usuario # Simplificación para el log
        else:
            print("[Sistema] Credenciales inválidas. Intente nuevamente.")

    # Bucle 2: Operaciones
    while autenticado:
        print("\n--- Panel de Control ---")
        accion = input("Presione 'A' para dar un Alta, o 'S' para salir: ").upper()
        
        if accion == 'S':
            break
        elif accion == 'A':
            paciente_id = input("Ingrese el ID o DNI del paciente a dar de alta: ")
            
            peticion_alta = PeticionAltaDTO(
                accion=AccionHospital.ALTA,
                origen=OrigenPeticion.MEDICO,
                paciente_id=paciente_id,
                medico_id=medico_id
            )
            
            print("[Sistema] Procesando alta... aguarde unos segundos.")
            # La terminal se quedará esperando aquí hasta que Celery termine
            respuesta = enviar_peticion(peticion_alta)
            
            if respuesta:
                print(f"\n[SISTEMA] {respuesta.get('mensaje')}")
                    
if __name__ == '__main__':
    main()