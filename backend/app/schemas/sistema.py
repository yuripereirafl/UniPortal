from pydantic import BaseModel

class SistemaBase(BaseModel):
    nome: str
    descricao: str | None = None
    status: str

class SistemaCreate(SistemaBase):
    pass

class Sistema(SistemaBase):
    id: int
    class Config:
        from_attributes = True
