from sqlalchemy import Column, Integer, String, Table, ForeignKey
from app.models.base import Base

class Setor(Base):
    __tablename__ = 'setores'
    __table_args__ = {'schema': 'rh_homologacao'}
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, nullable=True)
    nome = Column(String, nullable=False)
