from sqlalchemy import Column, Integer, Date, ForeignKey
from app.models.base import Base

class FuncionarioFilial(Base):
    __tablename__ = 'funcionario_filial'
    __table_args__ = {'schema': 'rh_homologacao'}
    funcionario_id = Column(Integer, ForeignKey('rh_homologacao.funcionarios.id'), primary_key=True)
    filial_id = Column(Integer, ForeignKey('rh_homologacao.filial.id'), primary_key=True)
    dt_inicio = Column(Date, primary_key=True)
    dt_fim = Column(Date, nullable=True)
