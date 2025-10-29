from pydantic import BaseModel, model_validator, ConfigDict
from typing import List, Optional


class FuncionarioSimple(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nome: str
    sobrenome: str
    email: Optional[str] = None


class GrupoPastaBase(BaseModel):
    nome: str
    descricao: Optional[str] = None


class GrupoPastaCreate(GrupoPastaBase):
    @model_validator(mode='before')
    def normalize(cls, values):
        nome = values.get('nome') if isinstance(values, dict) else None
        if nome is None:
            raise ValueError('nome é obrigatório')
        nome = nome.strip()
        if not nome:
            raise ValueError('nome não pode ser vazio')
        values['nome'] = nome
        return values


class GrupoPastaOut(GrupoPastaBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    funcionarios: List[FuncionarioSimple] = []
    qtd_participantes: int = 0

    @model_validator(mode='after')
    def compute_qtd(self):
        try:
            self.qtd_participantes = len(self.funcionarios or [])
        except Exception:
            self.qtd_participantes = 0
        return self
