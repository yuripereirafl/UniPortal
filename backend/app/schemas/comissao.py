"""
Schemas Pydantic para o módulo de Comissões
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class ProcedimentoComissaoBase(BaseModel):
    """Schema base para procedimento com valores de comissão"""
    mes_ref: date
    cod_exame: int
    descricao: Optional[str] = None
    valor: Optional[float] = None
    abrev: Optional[str] = None
    grupo: Optional[str] = None
    operadores: Optional[float] = None
    gerente: Optional[float] = None
    coord: Optional[float] = None
    super_: Optional[float] = Field(None, alias='super')  # 'super' é palavra reservada

    class Config:
        from_attributes = True
        populate_by_name = True


class ProcedimentoComissaoCreate(ProcedimentoComissaoBase):
    """Schema para criar novo procedimento"""
    pass


class ProcedimentoComissaoUpdate(BaseModel):
    """Schema para atualizar procedimento (todos campos opcionais)"""
    descricao: Optional[str] = None
    valor: Optional[float] = None
    abrev: Optional[str] = None
    grupo: Optional[str] = None
    operadores: Optional[float] = None
    gerente: Optional[float] = None
    coord: Optional[float] = None
    super_: Optional[float] = Field(None, alias='super')

    class Config:
        populate_by_name = True


class ProcedimentoComissaoResponse(ProcedimentoComissaoBase):
    """Schema de resposta para procedimento"""
    pass


class VendaComissaoItem(BaseModel):
    """Detalhamento de uma venda individual para cálculo de comissão"""
    cod_exame: int
    descricao: str
    grupo: str
    valor_procedimento: float
    valor_comissao: float
    data_agenda: Optional[date] = None
    paciente: Optional[str] = None


class ComissaoPorCategoria(BaseModel):
    """Comissão agregada por categoria (ODONTO, CHECK UP, etc)"""
    categoria: str
    quantidade_vendas: int
    valor_total_vendas: float
    valor_total_comissao: float
    vendas: Optional[List[VendaComissaoItem]] = []


class ComissaoColaboradorResponse(BaseModel):
    """Resposta completa do cálculo de comissão de um colaborador"""
    success: bool = True
    colaborador: dict  # {id_eyal, nome, cargo}
    mes_ref: str
    
    # Totais
    total_comissao: float = 0.0
    total_vendas: float = 0.0
    total_procedimentos: int = 0
    
    # Breakdown por categoria
    por_categoria: List[ComissaoPorCategoria] = []
    
    # Detalhamento conforme screenshot
    projecao_meta_realizada: float = 0.0  # Comissão baseada em vendas próprias
    campanhas: float = 0.0  # Comissão baseada em campanhas/bônus
    
    # Informações adicionais
    dias_trabalhados: Optional[int] = None
    meta_mes: Optional[float] = None
    realizado_mes: Optional[float] = None
    percentual_atingimento: Optional[float] = None


class ComissaoResumo(BaseModel):
    """Resumo simplificado de comissão (para cards)"""
    total_comissao: float
    projecao_meta: float
    campanhas: float
    quantidade_vendas: int


class ComissaoErroResponse(BaseModel):
    """Schema para resposta de erro"""
    success: bool = False
    error: str
    details: Optional[str] = None
