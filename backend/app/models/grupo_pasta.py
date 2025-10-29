from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

# Tabela de associação entre funcionário e grupo de pasta
funcionario_grupo_pasta = Table(
    'funcionario_grupo_pasta', Base.metadata,
    Column('funcionario_id', Integer, ForeignKey('rh_homologacao.funcionarios.id')),
    Column('grupo_pasta_id', Integer, ForeignKey('rh_homologacao.grupo_pasta.id')),
    schema='rh_homologacao'
)


class GrupoPasta(Base):
    __tablename__ = 'grupo_pasta'
    __table_args__ = {'schema': 'rh_homologacao'}
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    funcionarios = relationship('Funcionario', secondary=funcionario_grupo_pasta, back_populates='grupos_pasta')
