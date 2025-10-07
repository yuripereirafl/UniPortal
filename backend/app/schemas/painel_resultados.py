from pydantic import BaseModel
from datetime import date
from typing import Optional
from decimal import Decimal

class PainelResultadosBase(BaseModel):
    nome: str
    cargo: str
    nivel: Optional[str] = None
    unidade: str
    lider_direto: Optional[str] = None
    realizado_individual: Decimal
    realizado_final: Decimal
    id_eyal: str
    mes_ref: date
    cpf: str
    data_carga: date
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }

class PainelResultadosResponse(BaseModel):
    """Resposta com dados do painel de resultados"""
    colaborador: dict
    realizado: dict
    metadata: dict
    
    class Config:
        from_attributes = True
