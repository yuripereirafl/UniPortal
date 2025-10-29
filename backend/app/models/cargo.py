from sqlalchemy import Column, Integer, String
from app.models.base import Base

class Cargo(Base):
	__tablename__ = 'cargo'
	__table_args__ = {'schema': 'rh_homologacao'}
	id = Column(Integer, primary_key=True, index=True)
	funcao = Column(String, nullable=True)
	equipe = Column(String, nullable=True)
	nivel = Column(String, nullable=True)
	nome = Column(String, unique=True, nullable=False)
