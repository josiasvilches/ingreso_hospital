"""
Interfaz de consola para la seguridad en garita. 
Escanea (recibe) códigos de 6 caracteres y solicita su validación al servidor.
"""

import socket
import pickle
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modelos import PeticionValidacionDTO, AccionHospital, OrigenPeticion

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
    print("=== TERMINAL GARITA (PUNTO DE CONTROL) ===")
    
    while True:
        print("\n-----------------------------------")
        codigo = input("Escanee o ingrese el código de 6 caracteres (o 'S' para salir): ").upper()
        
        if codigo == 'S':
            break
            
        if len(codigo) != 6:
            print("[Error] El código debe tener exactamente 6 caracteres.")
            continue

        peticion = PeticionValidacionDTO(
            accion=AccionHospital.VALIDAR,
            origen=OrigenPeticion.GARITA,
            codigo=codigo
        )

        print("[Sistema] Validando con el servidor...")
        respuesta = enviar_peticion(peticion)

        if respuesta:
            if respuesta.get("status") == "ok":
                print("\n[ÉXITO] Vehículo autorizado.")
                print(f"-> Paciente: {respuesta.get('nombre')}")
                print(f"-> Habitación: {respuesta.get('habitacion')}")
            else:
                print(f"\n[DENEGADO] {respuesta.get('mensaje')}")

if __name__ == '__main__':
    main()