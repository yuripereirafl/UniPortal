from pydantic import BaseModel
from typing import Optional, List

class GrupoWhatsappBase(BaseModel):
    nome: str
    descricao: Optional[str] = None

class GrupoWhatsappCreate(GrupoWhatsappBase):
    pass

class GrupoWhatsappUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None

class GrupoWhatsapp(GrupoWhatsappBase):
    id: int
    
    class Config:
        from_attributes = True

class GrupoWhatsappWithFuncionarios(GrupoWhatsapp):
    funcionarios: List[dict] = []

    class Config:
        from_attributes = True
