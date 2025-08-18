from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class FuncionarioCargo(Base):
    __tablename__ = 'funcionario_cargo'
    __table_args__ = {'schema': 'rh_homologacao'}
    funcionario_id = Column(Integer, ForeignKey('rh_homologacao.funcionarios.id'), primary_key=True)
    cargo_id = Column(Integer, ForeignKey('rh_homologacao.cargo.id'), primary_key=True)
    dt_inicio = Column(Date, nullable=True)
    dt_fim = Column(Date, nullable=True)
    cargo_nome = Column(String, nullable=True)
    cargo_nivel = Column(String, nullable=True)
    cargo_funcao = Column(String, nullable=True)
    cargo_equipe = Column(String, nullable=True)

    funcionario = relationship('Funcionario', backref='cargos_vinculos')
    cargo = relationship('Cargo', backref='funcionarios_vinculos')
