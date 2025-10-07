# schemas/realizado.py
from pydantic import BaseModel
from typing import Optional
from datetime import date

class RealizadoColaborador(BaseModel):

    mes_ref : date
    id_eyal: int
    quem_agendou : Optional[str] = None
    unidade : Optional[str] = None
    tipo_grupo : Optional[str] = None
    total_registros : Optional[int] = None
    total_realizado : Optional[float] = None

    class Config:
        from_attributes = True