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

HOST = '127.0.0.1'
PORT = 8888

def enviar_peticion(dto):
    """Abre un socket, envía el DTO y espera la respuesta."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(pickle.dumps(dto))
            
            # Espera la respuesta del servidor
            datos_bytes = s.recv(1024)
            if datos_bytes:
                respuesta = pickle.loads(datos_bytes)
                return respuesta
    except ConnectionRefusedError:
        print("[Error] No se pudo conectar al Servidor Principal. ¿Está corriendo?")
        return None

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

    # Bucle 2: Operaciones (Altas)
    while autenticado:
        print("\n--- Panel de Control ---")
        accion = input("Presione 'A' (Alta), 'C' (Consultar códigos), o 'S' (Salir): ").upper()
        
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
            
            respuesta = enviar_peticion(peticion_alta)
            if respuesta:
                print(f"[Sistema] {respuesta.get('mensaje')}")
                
        elif accion == 'C':
            peticion_consulta = PeticionConsultaDTO(
                accion=AccionHospital.CONSULTAR_ALTAS,
                origen=OrigenPeticion.MEDICO,
                medico_id=medico_id
            )
            respuesta = enviar_peticion(peticion_consulta)
            if respuesta and respuesta.get("status") == "ok":
                datos = respuesta.get("datos", [])
                print("\n[Sistema] Códigos generados para sus pacientes:")
                if not datos:
                    print("  No hay códigos registrados aún.")
                for d in datos:
                    print(f"  -> Paciente: {d.get('paciente_id')} | Código: {d.get('codigo')} | Estado: {d.get('estado')}")
if __name__ == '__main__':
    main()