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

HOST = '127.0.0.1'
PORT = 8888

def enviar_peticion(dto):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(pickle.dumps(dto))
            datos_bytes = s.recv(1024)
            if datos_bytes:
                return pickle.loads(datos_bytes)
    except ConnectionRefusedError:
        print("[Error] Servidor inalcanzable.")
        return None

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