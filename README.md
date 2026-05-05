# Sistema Distribuido de Gestión Hospitalaria (Altas y Garitas)

Sistema concurrente y asíncrono desarrollado en Python para gestionar las altas de pacientes y la comunicación segura con las garitas de control en un hospital de alta masividad. 

Este proyecto fue diseñado para el examen final de Computación II, aplicando estrictamente herramientas de comunicación entre procesos (IPC) a nivel de sistema operativo y red, junto con patrones de diseño de software.

## Arquitectura y Tecnologías

El sistema opera mediante múltiples terminales independientes simulando diferentes nodos del hospital.

* **Core / Concurrencia:** `asyncio` (Event Loop) y `socket` (TCP nativo).
* **Mensajería / Serialización:** `pickle` (Data Transfer Objects).
* **IPC Local:** `multiprocessing.Pipe` (Autenticación aislada).
* **Asincronismo Externo:** `Celery` + `Redis` (Generación de códigos OTP en 2do plano).
* **Persistencia:** `MongoDB` (Operaciones atómicas `find_one_and_update`).
* **Patrones Implementados:** SOLID, DTO, Repository, Singleton, State, Centralized Enum, Chain of Responsibility.

## Estructura del Proyecto

```text
hospital_final/
├── docker-compose.yml       # Infraestructura externa (MongoDB y Redis)
├── requirements.txt         # Dependencias de Python
├── modelos.py               # Enums centralizados y DTOs de comunicación
├── servidor/                # Servidor asíncrono central (Router y Middlewares)
├── repositorio/             # Capa de acceso a datos y Singleton de MongoDB
├── procesos_locales/        # Subprocesos aislados (Pipe) para autenticación
├── workers/                 # Tareas en segundo plano (Celery)
└── terminales/              # Frontends TCP (Médico y Garita)
```

## Guía de Ejecución Paso a Paso

Dado que el sistema consta de múltiples procesos asíncronos e independientes, es necesario ejecutar cada componente en su propia terminal. Asegúrese de estar ubicado en la raíz del proyecto (`ingreso_hospital`) en todas ellas.

### 1. Preparación del Entorno
Antes de iniciar los scripts de Python, se debe activar el entorno virtual en las terminales correspondientes:
```bash
source venv/bin/activate
```
### 2. Despliegue de la Infraestructura
El sistema depende de una base de datos y un broker de mensajería aislados en contenedores.

Terminal 1 (Administración de Docker):
```
# Levantar los servicios en segundo plano (MongoDB en 27017, Redis en 6380)
sudo docker-compose up -d

# Verificar que los contenedores estén activos
sudo docker ps
```
(Nota: Esta terminal puede cerrarse una vez confirmada la ejecución de los contenedores).
### 3. Arranque de los Servicios Backend

El procesamiento en segundo plano y el enrutador principal deben estar activos antes de conectar a los clientes.

Terminal 2 (Worker de Celery):
Encargado de la generación asíncrona de códigos OTP, conectado de forma segura (fork-safe) a MongoDB.
```
celery -A workers.celery_app worker --loglevel=info
```

Terminal 3 (Servidor Principal y Middleware):
Levanta el Event Loop de asyncio, el túnel de comunicación local (IPC Pipe) y expone el puerto TCP para los clientes.
```
python3 servidor/main.py
```

### 4. Ejecución de Terminales Cliente (Interactivas)

Con el backend operativo, se inician las interfaces simuladas para el personal del hospital.

Terminal 4 (Frontend Médico):
Interfaz para la gestión de altas.
```
python3 terminales/app_medico.py
```
- Flujo de uso:

        Iniciar sesión (Ej: Usuario medico1, Contraseña 1234).

        Presionar A para cargar el DNI de un paciente y solicitar el alta.

        Esperar unos segundos y presionar C para consultar la base de datos y obtener el código OTP de 6 caracteres generado por Celery.

Terminal 5 (Frontend Garita):
Interfaz de control de seguridad para salida de vehículos.
```
python3 terminales/app_garita.py
```
Flujo de uso:

    Ingresar el código de 6 caracteres provisto por el médico.

    El sistema realizará una operación atómica en la base de datos para validar y "quemar" el código, garantizando que no pueda ser reutilizado.