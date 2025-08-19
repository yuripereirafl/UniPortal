from typing import List, Optional
from pydantic import BaseModel
from app.schemas.sistema import Sistema
from app.schemas.setor import SetorOut
from app.schemas.grupo_email import GrupoEmailOut
from .grupo_pasta import GrupoPastaOut
from app.schemas.cargo import CargoOut


class FuncionarioBase(BaseModel):
    cargo_id: Optional[int] = None
    nome: str
    sobrenome: str
    setores_ids: List[int] = []
    sistemas_ids: List[int] = []
    grupos_email_ids: List[int] = []
    grupos_pasta_ids: List[int] = []
    celular: Optional[str] = None
    email: Optional[str] = None
    data_admissao: str = ''
    data_inativado: str = ''
    cpf: Optional[str] = None
    data_afastamento: Optional[str] = None
    tipo_contrato: Optional[str] = None
    data_retorno: Optional[str] = None
    meta: Optional[str] = None
    tipo_pgto: Optional[str] = None

class FuncionarioCreate(FuncionarioBase):
    pass

class Funcionario(FuncionarioBase):
    id: int
    setores: List[SetorOut] = []
    sistemas: List[Sistema] = []
    grupos_email: List[GrupoEmailOut] = []
    grupos_pasta: List[GrupoPastaOut] = []
    cargo: Optional[str] = None
    data_admissao: str = ''
    data_inativado: str = ''
    cpf: Optional[str] = None
    data_afastamento: Optional[str] = None
    tipo_contrato: Optional[str] = None
    data_retorno: Optional[str] = None
class Config:
        from_attributes = True
