from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.base import Base

funcionario_grupo_email = Table(
    'funcionario_grupo_email', Base.metadata,
    Column('funcionario_id', Integer, ForeignKey('funcionarios.id', ondelete='CASCADE')),
    Column('grupo_email_id', Integer, ForeignKey('grupos_email.id', ondelete='RESTRICT')),
)
