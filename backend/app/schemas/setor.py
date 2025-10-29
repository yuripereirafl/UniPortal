from pydantic import BaseModel
from typing import Optional

class SetorBase(BaseModel):
    nome: str  # nome do setor
    descricao: Optional[str] = None

class SetorCreate(SetorBase):
    pass

class SetorUpdate(SetorBase):
    pass

class SetorOut(SetorBase):
    id: int
    class Config:
        from_attributes = True
