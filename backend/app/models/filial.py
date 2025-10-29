from sqlalchemy import Column, Integer, String
from app.models.base import Base

class Filial(Base):
    __tablename__ = 'filial'
    __table_args__ = {'schema': 'rh_homologacao'}
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    # Adicione outros campos conforme necessário
