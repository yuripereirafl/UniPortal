from sqlalchemy import Table, Column, Integer, ForeignKey
from app.models.base import Base

usuario_grupo = Table(
    'usuario_grupo', Base.metadata,
        Column('usuario_id', Integer, ForeignKey('rh_homologacao.usuarios.id', ondelete='CASCADE')),
    Column('grupo_id', Integer, ForeignKey('grupos.id', ondelete='CASCADE')),
)
