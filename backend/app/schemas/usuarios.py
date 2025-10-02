from pydantic import BaseModel
from typing import List
from app.schemas.permissoes import PermissaoOut

class UsuarioBase(BaseModel):
    username: str
    hashsenha: str
    setor_id: int | None = None

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioOut(UsuarioBase):
    id: int
    permissoes: List[PermissaoOut] = []
    setor: SetorOut | None = None
    class Config:
        from_attributes = True
