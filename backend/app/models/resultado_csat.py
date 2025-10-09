from sqlalchemy import Column, String, Integer, TIMESTAMP, DECIMAL
from app.models.base import Base

class ResultadoCSAT(Base):
    __tablename__ = 'resultadocsat'
    __table_args__ = {'schema': 'rh_homologacao'}
    
    # Chaves primárias compostas
    mes = Column(TIMESTAMP, primary_key=True, nullable=False)
    email = Column(String(255), primary_key=True, nullable=False)
    
    # Campos de identificação
    cod_usuario = Column(Integer)
    username = Column(String(100))
    nome = Column(String(255))
    ramal = Column(String(20))
    cpf = Column(String(14))
    equipe = Column(String(100))
    
    # Notas (1 a 5)
    nota_1 = Column(Integer)
    nota_2 = Column(Integer)
    nota_3 = Column(Integer)
    nota_4 = Column(Integer)
    nota_5 = Column(Integer)
    
    # Quantidades
    qtd_detrator = Column(Integer)
    qtd_neutro = Column(Integer)
    qtd_promotor = Column(Integer)
    qtd_tt = Column(Integer)  # Quantidade total
    
    # NPS - Net Promoter Score
    nps = Column(DECIMAL(5, 2))
    
    def __repr__(self):
        return f"<ResultadoCSAT(nome={self.nome}, mes={self.mes}, nps={self.nps})>"
