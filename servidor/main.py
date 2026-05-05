import asyncio
import pickle
import logging
import sys
import os
import socket
from multiprocessing import Pipe, Process

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from servidor.router import RouterDTO
from repositorio.conexion import ConexionMongo
from procesos.autenticador import proceso_autenticador

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class ServidorHospital:
    def __init__(self, port=8888):
        # Ya no recibimos 'host' por parámetro porque getaddrinfo lo calculará
        self.port = port
        self.db_conexion = ConexionMongo()
        
        # Implementación de IPC
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
        
        # Al omitir el host (o pasar None), asyncio usa getaddrinfo internamente.
        # Evalúa las familias y levanta dinámicamente 1 o 2 sockets (IPv4 e IPv6) 
        # resolviendo cualquier conflicto de condiciones de carrera.
        
        servidor = await asyncio.start_server(self.manejar_cliente, host=None, port=self.port)
        
        logging.info("--- Servidor Asíncrono Inicializado ---")
        
        # Leemos los sockets que asyncio decidió crear para confirmar las familias
        for sock in servidor.sockets:
            direccion = sock.getsockname()
            logging.info(f"Escuchando tráfico en la interfaz: {direccion}")
            
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