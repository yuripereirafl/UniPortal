from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.grupo_permissao import grupo_permissao

class Permissao(Base):
    __tablename__ = 'permissoes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(150), nullable=False, unique=True)
    descricao = Column(Text, nullable=True)

    grupos = relationship('Grupo', secondary=grupo_permissao, back_populates='permissoes')
