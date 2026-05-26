from sqlalchemy import Column, Integer, String
from app.models.base import Base

class Dominio(Base):
    __tablename__ = 'dominios'
    __table_args__ = {'schema': 'rh_homologacao'}

    id = Column(Integer, primary_key=True, index=True)
    dominio = Column(String, unique=True, index=True, nullable=False)
    data_vencimento = Column(String, nullable=False)
    hospedagem = Column(String, nullable=True)
    provedor = Column(String, nullable=True)
