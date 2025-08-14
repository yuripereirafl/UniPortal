from sqlalchemy import Column, Integer, String
from app.models.base import Base

class Cargo(Base):
    __tablename__ = 'cargos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False, unique=True)
    descricao = Column(String, nullable=True)