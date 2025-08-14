from sqlalchemy import Column, Integer, String
from app.models.base import Base

class Filial(Base):
    __tablename__ = 'filial'
    id = Column(Integer, primary_key=True, autoincrement=True)
    unidade = Column(String, nullable=False, unique=True)
