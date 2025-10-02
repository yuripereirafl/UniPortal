from sqlalchemy import Column, Integer, String
from app.models.base import Base


class GrupoEmail(Base):
    __tablename__ = 'grupos_email'
    __table_args__ = {'schema': 'rh_homologacao'}
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, nullable=False)
