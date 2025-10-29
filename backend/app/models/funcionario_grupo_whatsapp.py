from sqlalchemy import Column, BigInteger, ForeignKey, Table
from app.models.base import Base

# Tabela de associação para relacionamento many-to-many
funcionario_grupo_whatsapp = Table(
    'funcionario_grupo_whtss',
    Base.metadata,
    Column('funcionario_id', BigInteger, ForeignKey('rh_homologacao.funcionarios.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True),
    Column('grupo_whtss_id', BigInteger, ForeignKey('rh_homologacao.grupos_whtss.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True),
    schema='rh_homologacao'
)
