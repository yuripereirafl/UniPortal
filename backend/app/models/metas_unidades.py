from sqlalchemy import Column, String, Integer, Float, Date
from app.models.base import Base

class MetaUnidade(Base):
    """
    Representa a tabela 'metas_unidades' no banco de dados.
    Contém as metas estabelecidas para cada unidade.
    """
    __tablename__ = 'metas_unidades'
    __table_args__ = {'schema': 'rh_homologacao'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    unidade = Column(String, nullable=False)
    mes_ref = Column(String, nullable=False)
    meta_total = Column(Float)
    meta_odonto = Column(Float)
    meta_checkup = Column(Float)
    meta_dr_central = Column(Float)
    meta_babyclick = Column(Float)
    data_criacao = Column(Date)
    data_atualizacao = Column(Date)
    ativo = Column(String, default='S')