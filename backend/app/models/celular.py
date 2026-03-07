from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.funcionario import Funcionario
from app.models.setor import Setor

class CelularLinha(Base):
    __tablename__ = 'celulares_linhas'
    __table_args__ = {'schema': 'rh_homologacao'}

    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String, nullable=True)
    modelo = Column(String, nullable=True)
    imei = Column(String, unique=True, nullable=True)
    numero_chip = Column(String, nullable=True)
    plano = Column(String, nullable=True)
    tipo_pagamento = Column(String, nullable=True) # Pré ou Pós
    whatsapp = Column(String, nullable=True)
    bloqueio = Column(String, nullable=True) # Pode ser o texto "2023", "OK", etc conforme planilha
    
    # Relacionamentos
    funcionario_id = Column(Integer, ForeignKey('rh_homologacao.funcionarios.id'), nullable=True)
    setor_id = Column(Integer, ForeignKey('rh_homologacao.setores.id'), nullable=True)
    
    funcionario = relationship("Funcionario", backref="celulares_linhas")
    setor = relationship("Setor", backref="celulares_linhas")

class CelularConta(Base):
    __tablename__ = 'celulares_contas'
    __table_args__ = {'schema': 'rh_homologacao'}

    id = Column(Integer, primary_key=True, index=True)
    gmail = Column(String, nullable=False)
    senha = Column(String, nullable=True)
    
    # Registro associado
    celular_id = Column(Integer, ForeignKey('rh_homologacao.celulares_linhas.id'), nullable=True)
    funcionario_id = Column(Integer, ForeignKey('rh_homologacao.funcionarios.id'), nullable=True)
    
    celular = relationship("CelularLinha", backref="contas")
    funcionario = relationship("Funcionario", backref="celulares_contas")
