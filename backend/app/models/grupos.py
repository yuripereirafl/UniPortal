from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.grupo_permissao import grupo_permissao

class Grupo(Base):
    __tablename__ = 'grupos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False, unique=True)
    descricao = Column(String, nullable=True)

    permissoes = relationship('Permissao', secondary=grupo_permissao, back_populates='grupos')
