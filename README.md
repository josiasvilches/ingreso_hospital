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