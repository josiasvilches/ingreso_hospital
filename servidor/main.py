"""
[Facade] Levanta el event loop de asyncio y el socket TCP.
Sirve como punto de entrada a todo el backend.
"""
import asyncio
import pickle
import logging
import sys
import os
from multiprocessing import Pipe, Process

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from servidor.router import RouterDTO
from repositorio.conexion import ConexionMongo
from procesos.autenticador import proceso_autenticador

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class ServidorHospital:
    def __init__(self, host='127.0.0.1', port=8888):
        self.host = host
        self.port = port
        self.db_conexion = ConexionMongo()
        
        # Implementación de IPC: Se crean los dos extremos del túnel de comunicación
        self.pipe_receptor, self.pipe_emisor = Pipe()
        self.proceso_auth = Process(target=proceso_autenticador, args=(self.pipe_receptor,))
        
        # Inyección de dependencias
        self.router = RouterDTO(self.db_conexion, self.pipe_emisor)

    async def manejar_cliente(self, reader, writer):
        direccion = writer.get_extra_info('peername')
        logging.info(f"[+] Nueva conexión establecida desde {direccion}")
        
        try:
            while True:
                datos_bytes = await reader.read(4096)
                if not datos_bytes:
                    break
                    
                dto = pickle.loads(datos_bytes)
                
                # Desacopla las operaciones sincrónicas (BD/Pipe) del Event Loop usando hilos temporales
                respuesta = await asyncio.to_thread(self.router.enrutar, dto)
                
                writer.write(pickle.dumps(respuesta))
                await writer.drain()
                
        except ConnectionResetError:
            pass
        except Exception as e:
            logging.error(f"Error procesando cliente {direccion}: {e}")
        finally:
            logging.info(f"[-] Conexión cerrada: {direccion}")
            writer.close()
            await writer.wait_closed()

    async def iniciar(self):
        # Levantar el subproceso antes de abrir el servidor de red
        self.proceso_auth.start()
        
        servidor = await asyncio.start_server(self.manejar_cliente, self.host, self.port)
        logging.info(f"Servidor Asíncrono inicializado. Escuchando en TCP {self.host}:{self.port}")
        
        async with servidor:
            await servidor.serve_forever()

if __name__ == '__main__':
    server = ServidorHospital()
    try:
        asyncio.run(server.iniciar())
    except KeyboardInterrupt:
        logging.info("Apagando servidor y cerrando subprocesos...")
        server.proceso_auth.terminate()
        server.proceso_auth.join()