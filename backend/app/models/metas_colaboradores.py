from sqlalchemy import Column, String, Integer, Float, Date
from app.models.base import Base

# NOME DA CLASSE ALTERADO PARA O SINGULAR: MetaColaborador
class MetaColaborador(Base):
    """
    Representa a tabela 'metas_colaboradores' no banco de dados.
    """
    __tablename__ = 'metas_colaboradores'
    __table_args__ = {'schema': 'rh_homologacao'}

    mes_ref = Column(String, primary_key=True)
    cpf = Column(String, primary_key=True)
    nome = Column(String)
    unidade = Column(String)
    equipe = Column(String)
    lider_direto = Column(String)
    cargo = Column(String)
    nivel = Column(String)
    funcao = Column(String)
    dias_trabalhados = Column(Integer)
    dias_de_falta = Column(Integer)
    meta_final = Column(Float)
    meta_diaria = Column(Float)
    data_criacao = Column(Date)
    id_eyal = Column(String)
