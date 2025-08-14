
from sqlalchemy import Column, Integer, String
from app.models.base import Base

class Sistema(Base):
    __tablename__ = 'sistemas'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    status = Column(String, nullable=False)

