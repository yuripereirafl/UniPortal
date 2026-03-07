from pydantic import BaseModel
from typing import Optional, List

# --- CELULAR LINHA ---

class CelularLinhaBase(BaseModel):
    marca: Optional[str] = None
    modelo: Optional[str] = None
    imei: Optional[str] = None
    numero_chip: Optional[str] = None
    plano: Optional[str] = None
    tipo_pagamento: Optional[str] = None
    whatsapp: Optional[str] = None
    bloqueio: Optional[str] = None
    funcionario_id: Optional[int] = None
    setor_id: Optional[int] = None

class CelularLinhaCreate(CelularLinhaBase):
    pass

class CelularLinhaUpdate(CelularLinhaBase):
    pass

class CelularLinha(CelularLinhaBase):
    id: int
    
    class Config:
        from_attributes = True

# --- CELULAR CONTA ---

class CelularContaBase(BaseModel):
    gmail: str
    senha: Optional[str] = None
    celular_id: Optional[int] = None
    funcionario_id: Optional[int] = None

class CelularContaCreate(CelularContaBase):
    pass

class CelularContaUpdate(CelularContaBase):
    pass

class CelularConta(CelularContaBase):
    id: int
    
    class Config:
        from_attributes = True

# --- EXTRAS ---

class CelularLinhaComContas(CelularLinha):
    contas: List[CelularConta] = []
