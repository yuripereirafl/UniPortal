from pydantic import BaseModel
from typing import Optional

class DominioBase(BaseModel):
    dominio: str
    data_vencimento: str
    hospedagem: Optional[str] = None
    provedor: Optional[str] = None

class DominioCreate(DominioBase):
    pass

class DominioUpdate(DominioBase):
    pass

class DominioResponse(DominioBase):
    id: int

    class Config:
        from_attributes = True
