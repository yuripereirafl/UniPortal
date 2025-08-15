from pydantic import BaseModel

class GrupoPastaBase(BaseModel):
    nome: str
    descricao: str | None = None

class GrupoPastaCreate(GrupoPastaBase):
    pass

class GrupoPastaOut(GrupoPastaBase):
    id: int
    class Config:
        from_attributes = True
