"""
[Centralized Enum / DTOs]
Contiene las enumeraciones y los DTOs (Data Transfer Objects) 
para transportar información limpia entre las distintas capas.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional

# --- CENTRALIZED ENUMS ---

class EstadoCodigo(Enum):
    PENDIENTE = "pendiente"
    USADO = "usado"
    EXPIRADO = "expirado"

class AccionHospital(Enum):
    AUTENTICAR = "autenticar"
    ALTA = "alta"
    VALIDAR = "validar"

class OrigenPeticion(Enum):
    MEDICO = "medico"
    GARITA = "garita"

# --- DATA TRANSFER OBJECTS (DTOs) ---
# Usamos herencia para mantener la base unificada (Polimorfismo básico)

@dataclass
class PeticionBaseDTO:
    accion: AccionHospital
    origen: OrigenPeticion

@dataclass
class PeticionAutenticacionDTO(PeticionBaseDTO):
    usuario: str
    password: str

@dataclass
class PeticionAltaDTO(PeticionBaseDTO):
    paciente_id: str
    medico_id: str

@dataclass
class PeticionValidacionDTO(PeticionBaseDTO):
    codigo: str

@dataclass
class RespuestaDTO:
    status: str  # "ok" o "error"
    mensaje: str
    datos: Optional[dict] = None  # Para enviar info extra como el nombre y habitación