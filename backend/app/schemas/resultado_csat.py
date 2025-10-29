from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ResultadoCSATBase(BaseModel):
    mes: datetime
    email: str
    cod_usuario: Optional[int] = None
    username: Optional[str] = None
    nome: Optional[str] = None
    ramal: Optional[str] = None
    cpf: Optional[str] = None
    equipe: Optional[str] = None
    nota_1: Optional[int] = None
    nota_2: Optional[int] = None
    nota_3: Optional[int] = None
    nota_4: Optional[int] = None
    nota_5: Optional[int] = None
    qtd_detrator: Optional[int] = None
    qtd_neutro: Optional[int] = None
    qtd_promotor: Optional[int] = None
    qtd_tt: Optional[int] = None
    nps: Optional[Decimal] = None

    class Config:
        from_attributes = True


class ResultadoCSATResponse(BaseModel):
    """Schema para resposta da API de NPS"""
    success: bool
    colaborador: dict
    nps_data: dict
    message: Optional[str] = None

    class Config:
        from_attributes = True
