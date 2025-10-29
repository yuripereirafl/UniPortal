
from sqlalchemy import Column, Integer, String
from app.models.base import Base


class Sistema(Base):
    __tablename__ = 'sistemas'
    __table_args__ = {'schema': 'rh_homologacao'}
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    status = Column(String, nullable=False)

