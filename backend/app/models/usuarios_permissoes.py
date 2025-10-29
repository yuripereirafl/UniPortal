from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.base import Base

usuarios_permissoes = Table(
    'usuarios_permissoes', Base.metadata,
        Column('usuario_id', Integer, ForeignKey('rh_homologacao.usuarios.id', ondelete='CASCADE')),
    Column('permissao_id', Integer, ForeignKey('permissoes.id', ondelete='CASCADE'))
)
