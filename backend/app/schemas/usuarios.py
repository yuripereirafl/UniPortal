from pydantic import BaseModel
from typing import List
from app.schemas.permissoes import PermissaoOut

class UsuarioBase(BaseModel):
    username: str
    hashsenha: str

class UsuarioCreate(UsuarioBase):
    pass

class UsuarioOut(UsuarioBase):
    id: int
    permissoes: List[PermissaoOut] = []
    class Config:
        from_attributes = True
