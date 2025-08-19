from typing import List, Optional, Union
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
    motivo_afastamento: Optional[str] = None
    meta: Optional[Union[float, str]] = None  # Aceita tanto float quanto string
    tipo_pgto: Optional[str] = None

class FuncionarioCreate(FuncionarioBase):
    pass

class FuncionarioUpdate(BaseModel):
    """Schema para atualizações - todos os campos são opcionais"""
    cargo_id: Optional[int] = None
    # Campos separados do cargo
    cargo_nome: Optional[str] = None
    cargo_funcao: Optional[str] = None
    cargo_equipe: Optional[str] = None
    cargo_nivel: Optional[str] = None
    nome: Optional[str] = None
    sobrenome: Optional[str] = None
    setores_ids: Optional[List[int]] = None
    sistemas_ids: Optional[List[int]] = None
    grupos_email_ids: Optional[List[int]] = None
    grupos_pasta_ids: Optional[List[int]] = None
    celular: Optional[str] = None
    email: Optional[str] = None
    data_admissao: Optional[str] = None
    data_inativado: Optional[str] = None
    cpf: Optional[str] = None
    data_afastamento: Optional[str] = None
    tipo_contrato: Optional[str] = None
    data_retorno: Optional[str] = None
    motivo_afastamento: Optional[str] = None
    meta: Optional[Union[float, str]] = None
    tipo_pgto: Optional[str] = None

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
    motivo_afastamento: Optional[str] = None
class Config:
        from_attributes = True
