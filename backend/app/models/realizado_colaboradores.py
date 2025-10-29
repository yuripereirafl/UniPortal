from sqlalchemy import Column, Integer, Date, Numeric, TIMESTAMP, String
from app.models.base import Base

class RealizadoColaborador(Base):
    """
    Representa a tabela 'realizado_colaborador' no banco de dados.
    """
    __tablename__ = 'realizado_colaborador'
    __table_args__ = {'schema': 'rh_homologacao'}

    # AJUSTE A CHAVE PRIMÁRIA AQUI
    mes_ref = Column(Date, primary_key=True)
    id_eyal = Column(Integer, primary_key=True)
    unidade = Column(String(255), primary_key=True) 
    tipo_grupo = Column(String(50), primary_key=True) 
    quem_agendou = Column(String(255))
    total_registros = Column(Integer)
    total_realizado = Column(Numeric(15, 2))
    data_atualizacao = Column(TIMESTAMP(timezone=True))