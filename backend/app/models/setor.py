from sqlalchemy import Column, Integer, String
from app.models.base import Base

class Setor(Base):
    __tablename__ = 'setores'
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, nullable=True)
    nome = Column(String, nullable=False)
