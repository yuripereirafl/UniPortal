from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.base import Base

funcionario_grupo_pasta = Table(
    'funcionario_grupo_pasta', Base.metadata,
    Column('funcionario_id', Integer, ForeignKey('funcionarios.id', ondelete='CASCADE')),
    Column('grupo_pasta_id', Integer, ForeignKey('grupo_pasta.id', ondelete='RESTRICT')),
)
