"""
Modelo para tabela de Pagamentos de Meta
Armazena cálculos mensais de pagamento baseado em performance e NPS
"""
from sqlalchemy import Column, String, Date, Numeric, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from app.models.base import Base

class PagamentoMeta(Base):
    __tablename__ = "pagamentos_meta"
    __table_args__ = {'schema': 'rh_homologacao'}

    # Chave composta
    mes_ref = Column(Date, primary_key=True, nullable=False)
    id_eyal = Column(Text, primary_key=True, nullable=False)

    # Dados do colaborador
    nome = Column(Text)
    cargo = Column(Text)
    unidade_api = Column(Text)
    equipe_banco = Column(Text)

    # Métricas de performance
    percentual_projetado_usado = Column(Numeric(10, 2))
    nps = Column(Numeric(10, 2))
    status = Column(Text)

    # Cálculo de pagamento
    itens_calculados = Column(Text)  # JSON ou texto descritivo
    coluna_faixa_pagamento = Column(Text)
    pagamento_base_total = Column(Numeric(12, 2))
    bonus_ativo = Column(Boolean)
    pagamento_final = Column(Numeric(12, 2))

    def __repr__(self):
        return f"<PagamentoMeta(mes={self.mes_ref}, id_eyal={self.id_eyal}, pagamento_final={self.pagamento_final})>"
