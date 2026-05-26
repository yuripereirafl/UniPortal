from pydantic import BaseModel
from typing import Optional

class NotebookBase(BaseModel):
    patrimonio: Optional[str] = None
    modelo: Optional[str] = None
    data_entrega: Optional[str] = None
    funcionario_id: Optional[int] = None
    setor_id: Optional[int] = None

class NotebookCreate(NotebookBase):
    pass

class NotebookUpdate(NotebookBase):
    pass

class NotebookResponse(NotebookBase):
    id: int

    class Config:
        from_attributes = True
