from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.funcionario import Funcionario
from app.models.setor import Setor

class Notebook(Base):
    __tablename__ = 'notebooks'
    __table_args__ = {'schema': 'rh_homologacao'}

    id = Column(Integer, primary_key=True, index=True)
    patrimonio = Column(String, unique=True, index=True, nullable=True)
    modelo = Column(String, nullable=True)
    data_entrega = Column(String, nullable=True)

    # Relacionamentos
    funcionario_id = Column(Integer, ForeignKey('rh_homologacao.funcionarios.id'), nullable=True)
    setor_id = Column(Integer, ForeignKey('rh_homologacao.setores.id'), nullable=True)

    funcionario = relationship("Funcionario", backref="notebooks")
    setor = relationship("Setor", backref="notebooks")
