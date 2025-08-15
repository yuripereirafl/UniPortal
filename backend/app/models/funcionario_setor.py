from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.base import Base

funcionario_setor = Table(
    'funcionario_setor',
    Base.metadata,
    Column('funcionario_id', Integer, ForeignKey('funcionarios.id'), primary_key=True),
    Column('setor_id', Integer, ForeignKey('setores.id'), primary_key=True)
)
