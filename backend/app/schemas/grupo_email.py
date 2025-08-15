from pydantic import BaseModel

class GrupoEmailBase(BaseModel):
    nome: str

class GrupoEmailCreate(GrupoEmailBase):
    pass

class GrupoEmailOut(GrupoEmailBase):
    id: int
    class Config:
        orm_mode = True
        from_attributes = True
