from sqlalchemy import Column, Integer, Date, ForeignKey, Text
from app.models.base import Base

class FuncionarioMeta(Base):
    __tablename__ = 'funcionario_meta'
    __table_args__ = {'schema': 'rh_homologacao'}
    funcionario_id = Column(Integer, ForeignKey('rh_homologacao.funcionarios.id'), primary_key=True)
    meta_id = Column(Integer, ForeignKey('rh_homologacao.meta.id'), primary_key=True)
    dt_inicio = Column(Date, primary_key=True)
    dt_fim = Column(Date, nullable=True)
    observacao = Column(Text, nullable=True)
