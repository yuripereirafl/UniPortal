from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.base import Base

usuario_unidade = Table(
    'usuario_unidade',
    Base.metadata,
        Column('usuario_id', Integer, ForeignKey('rh_homologacao.usuarios.id', ondelete='CASCADE')),
    Column('filial_id', Integer, ForeignKey('filial.id', ondelete='CASCADE'))
)
