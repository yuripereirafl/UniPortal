# schemas/metas.py
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime  # Importar datetime também

class MetaColaborador(BaseModel):
    """
    Schema Pydantic para validar e formatar os dados de metas dos colaboradores.
    """
    # Alterado para aceitar o tipo date diretamente do banco
    mes_ref: date
    cpf: str
    nome: Optional[str] = None
    unidade: Optional[str] = None
    equipe: Optional[str] = None
    lider_direto: Optional[str] = None
    cargo: Optional[str] = None
    nivel: Optional[str] = None
    funcao: Optional[str] = None
    dias_trabalhados: Optional[float] = None
    dias_de_falta: Optional[int] = None
    meta_final: Optional[float] = None
    meta_diaria: Optional[float] = None
    data_criacao: Optional[datetime] = None
    id_eyal: Optional[str] = None

    class Config:
        # Permite que o Pydantic leia os dados diretamente de um objeto SQLAlchemy
        from_attributes = True