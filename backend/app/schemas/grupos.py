from pydantic import BaseModel

class GrupoBase(BaseModel):
    nome: str
    descricao: str | None = None

class GrupoCreate(GrupoBase):
    pass

class GrupoOut(GrupoBase):
    id: int
    class Config:
        from_attributes = True
