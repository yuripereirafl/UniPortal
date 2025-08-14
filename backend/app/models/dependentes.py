from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.models.base import Base

class Dependente(Base):
    __tablename__ = 'dependentes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    funcionario_id = Column(Integer, ForeignKey('funcionarios.id', ondelete='CASCADE'))
    nome = Column(String, nullable=False)
    parentesco = Column(String, nullable=True)
    cpf = Column(String, nullable=True)
    data_nascimento = Column(Date, nullable=True)
