from pydantic import BaseModel
from typing import Optional
from datetime import date

class OrcamentoBase(BaseModel):
    seq_orcamento: int
    cod_usuario: Optional[int] = None
    cod_paciente: Optional[int] = None
    cod_agenda: Optional[int] = None
    criado: Optional[date] = None
    data_agenda: Optional[date] = None
    confirmado: Optional[str] = None
    procedimento: Optional[str] = None
    colab_orcou: Optional[str] = None
    unidade_usuario: Optional[str] = None
    nome_base: Optional[str] = None
    rn_final: Optional[int] = None
    
    class Config:
        from_attributes = True


class OrcamentoResponse(BaseModel):
    """Resposta com dados de orçamentos do colaborador"""
    success: bool
    colaborador: dict
    orcamentos: dict
    message: Optional[str] = None
    
    class Config:
        from_attributes = True
