from pydantic import BaseModel

class CargoBase(BaseModel):
    funcao: str | None = None
    equipe: str | None = None
    nivel: str | None = None
    nome: str

class CargoCreate(CargoBase):
    pass

class CargoOut(CargoBase):
    id: int

    class Config:
        orm_mode = True
