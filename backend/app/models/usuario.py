from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.base import Base

usuario_setor = Table(
    'usuario_setor',
    Base.metadata,
    Column('usuario_id', Integer, ForeignKey('rh_homologacao.usuarios.id'), primary_key=True),
    Column('setor_id', Integer, ForeignKey('rh_homologacao.setores.id'), primary_key=True),
    schema='rh_homologacao'
)

from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from .usuario_grupo import usuario_grupo

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "rh_homologacao"}
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column("hashsenha", String, nullable=False)
    id_funcionario = Column(Integer, nullable=True)
    setores = relationship('Setor', secondary=usuario_setor, backref='usuarios')
    grupos = relationship('Grupo', secondary=usuario_grupo, back_populates='usuarios', passive_deletes=True)
