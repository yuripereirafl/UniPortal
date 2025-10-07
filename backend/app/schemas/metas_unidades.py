from pydantic import BaseModel
from typing import Optional, List
from datetime import date

class MetaUnidadeBase(BaseModel):
    unidade: str
    mes_ref: str
    meta_total: Optional[float] = None
    meta_odonto: Optional[float] = None
    meta_checkup: Optional[float] = None
    meta_dr_central: Optional[float] = None
    meta_babyclick: Optional[float] = None

class MetaUnidadeCreate(MetaUnidadeBase):
    pass

class MetaUnidadeUpdate(MetaUnidadeBase):
    unidade: Optional[str] = None
    mes_ref: Optional[str] = None

class MetaUnidadeResponse(MetaUnidadeBase):
    id: int
    data_criacao: Optional[date] = None
    data_atualizacao: Optional[date] = None
    ativo: Optional[str] = None

    class Config:
        from_attributes = True

class DashboardUnidadeResponse(BaseModel):
    """Schema para resposta do dashboard da unidade"""
    unidade: str
    mes_ref: str
    
    # Metas
    meta_total: float
    meta_odonto: Optional[float] = None
    meta_checkup: Optional[float] = None
    meta_dr_central: Optional[float] = None
    meta_babyclick: Optional[float] = None
    
    # Realizados (serão calculados)
    realizado_total: float
    realizado_odonto: Optional[float] = None
    realizado_checkup: Optional[float] = None
    realizado_dr_central: Optional[float] = None
    realizado_babyclick: Optional[float] = None
    
    # Indicadores calculados
    percentual_total: float
    percentual_odonto: Optional[float] = None
    percentual_checkup: Optional[float] = None
    percentual_dr_central: Optional[float] = None
    percentual_babyclick: Optional[float] = None
    
    # Informações adicionais
    total_colaboradores: int
    colaboradores_ativos: int
    
    class Config:
        from_attributes = True

# Schema para resposta individual de unidade no dashboard geral
class UnidadeResponse(BaseModel):
    id: int
    unidade: str
    mes: str
    meta: float
    realizado: float
    diferenca: float
    percentual_atingimento: float
    
    class Config:
        from_attributes = True

# Schema para resumo geral do dashboard
class ResumoGeralResponse(BaseModel):
    total_unidades: int
    meta_total: float
    realizado_total: float
    percentual_medio: float
    
    class Config:
        from_attributes = True

# Schema para resposta do dashboard geral
class DashboardGeralResponse(BaseModel):
    unidades: List[UnidadeResponse]
    resumo: ResumoGeralResponse
    
    class Config:
        from_attributes = True