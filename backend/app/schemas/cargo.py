from pydantic import BaseModel

class CargoBase(BaseModel):
    nome: str
    descricao: str | None = None

class CargoCreate(CargoBase):
    pass

class CargoOut(CargoBase):
    id: int
    class Config:
        from_attributes = True