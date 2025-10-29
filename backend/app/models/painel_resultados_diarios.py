from sqlalchemy import Column, String, Date, DECIMAL
from app.models.base import Base

class PainelResultadosDiarios(Base):
    __tablename__ = 'painelresultadosdiarios'
    __table_args__ = {'schema': 'rh_homologacao'}
    
    # Campos da tabela
    nome = Column(String(255))
    cargo = Column(String(255))
    nivel = Column(String(100))
    unidade = Column(String(255))
    lider_direto = Column(String(255))
    realizado_individual = Column(DECIMAL(18, 2))
    realizado_final = Column(DECIMAL(18, 2))
    id_eyal = Column(String(50))
    mes_ref = Column(Date)
    
    # Chave primária composta
    cpf = Column(String(14), primary_key=True, nullable=False)
    data_carga = Column(Date, primary_key=True, nullable=False)
    
    def __repr__(self):
        return f"<PainelResultadosDiarios(cpf={self.cpf}, nome={self.nome}, data_carga={self.data_carga})>"
