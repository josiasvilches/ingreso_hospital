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
    CONSULTAR_ALTAS = "consultar_altas"

class OrigenPeticion(Enum):
    MEDICO = "medico"
    GARITA = "garita"

# --- DATA TRANSFER OBJECTS (DTOs) ---

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
class PeticionConsultaDTO(PeticionBaseDTO):
    medico_id: str

@dataclass
class RespuestaDTO:
    status: str  
    mensaje: str
    datos: Optional[dict] = None