from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, func
from .base import Base

class SlaRule(Base):
    __tablename__ = "sla_rules"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, unique=True, index=True)
    criticidade = Column(String)
    tempo_limite_minutos = Column(Integer)
    etapas_audit = Column(Integer, default=0)

class TicketSla(Base):
    __tablename__ = "tickets_sla"

    id = Column(Integer, primary_key=True, index=True)
    glpi_id = Column(Integer, unique=True, index=True)
    titulo = Column(String)
    categoria = Column(String)
    data_abertura = Column(DateTime)
    data_fechamento = Column(DateTime, nullable=True)
    tempo_atendimento_minutos = Column(Integer, default=0)
    status_sla = Column(String) # SLA OK / SLA NÃO OK
    tecnico = Column(String, nullable=True)
    requerente = Column(String, nullable=True)
    mes_referencia = Column(String) # YYYY-MM
    etapas_total = Column(Integer, default=0)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_audited = Column(Boolean, default=False)
