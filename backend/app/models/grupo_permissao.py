from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.base import Base

grupo_permissao = Table(
    'grupo_permissao', Base.metadata,
    Column('grupo_id', Integer, ForeignKey('grupos.id', ondelete='CASCADE')),
    Column('permissao_id', Integer, ForeignKey('permissoes.id', ondelete='CASCADE')),
)
