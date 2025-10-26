"""
Schemas Pydantic para Pagamentos de Meta
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from decimal import Decimal


class PagamentoMetaBase(BaseModel):
    """Schema base para pagamento de meta"""
    mes_ref: date
    id_eyal: str
    nome: Optional[str] = None
    cargo: Optional[str] = None
    unidade_api: Optional[str] = None
    equipe_banco: Optional[str] = None
    percentual_projetado_usado: Optional[Decimal] = None
    nps: Optional[Decimal] = None
    status: Optional[str] = None
    itens_calculados: Optional[str] = None
    coluna_faixa_pagamento: Optional[str] = None
    pagamento_base_total: Optional[Decimal] = None
    bonus_ativo: Optional[bool] = None
    pagamento_final: Optional[Decimal] = None

    class Config:
        from_attributes = True


class PagamentoMetaResponse(PagamentoMetaBase):
    """Schema de resposta para consulta de pagamento"""
    pass


class PagamentoResumo(BaseModel):
    """Resumo simplificado do pagamento (para integração com comissão)"""
    pagamento_final: float = 0.0
    percentual_projetado: float = 0.0
    nps: float = 0.0
    status: Optional[str] = None
    bonus_ativo: bool = False
