from pydantic import BaseModel
from typing import Optional
from datetime import date

class FuncionarioCargoBase(BaseModel):
    funcionario_id: int
    cargo_id: int
    dt_inicio: Optional[date] = None
    dt_fim: Optional[date] = None
    cargo_nome: Optional[str] = None
    cargo_nivel: Optional[str] = None
    cargo_funcao: Optional[str] = None
    cargo_equipe: Optional[str] = None

class FuncionarioCargoCreate(FuncionarioCargoBase):
    pass

class FuncionarioCargoRead(FuncionarioCargoBase):
    pass

    class Config:
        orm_mode = True
