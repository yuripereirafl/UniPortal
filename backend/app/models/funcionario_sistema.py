from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.base import Base

funcionario_sistema = Table(
    'funcionario_sistema', Base.metadata,
    Column('funcionario_id', Integer, ForeignKey('funcionarios.id', ondelete='CASCADE')),
    Column('sistema_id', Integer, ForeignKey('sistemas.id', ondelete='RESTRICT')),
)
