from pydantic import BaseModel

class PermissaoBase(BaseModel):
    codigo: str
    descricao: str | None = None

class PermissaoCreate(PermissaoBase):
    pass

class PermissaoOut(PermissaoBase):
    codigo: str
    class Config:
        from_attributes = True
