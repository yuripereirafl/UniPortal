from sqlalchemy import Column, String, Date, Integer, BIGINT, CHAR, TEXT
from app.models.base import Base

class Orcamento(Base):
    __tablename__ = 'orcamentos'
    __table_args__ = {'schema': 'rh_homologacao'}
    
    # Chave primária
    seq_orcamento = Column(BIGINT, primary_key=True, nullable=False)
    
    # Campos de identificação
    cod_usuario = Column(Integer)
    cod_paciente = Column(Integer)
    cod_agenda = Column(Integer)
    
    # Datas
    criado = Column(Date)
    data_agenda = Column(Date)
    
    # Status
    confirmado = Column(CHAR(1))  # 'S' ou 'N'
    
    # Informações do orçamento
    procedimento = Column(TEXT)
    colab_orcou = Column(TEXT)  # Nome do colaborador que orçou
    unidade_usuario = Column(TEXT)
    nome_base = Column(TEXT)
    rn_final = Column(Integer)
    
    def __repr__(self):
        return f"<Orcamento(seq={self.seq_orcamento}, cod_usuario={self.cod_usuario}, criado={self.criado})>"
