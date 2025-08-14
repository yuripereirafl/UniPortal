from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from ..database import Base

class User(Base):
    __tablename__ = 'usuarios'
    __table_args__ = {'extend_existing': True, 'schema': 'rh_homologacao'}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashsenha = Column(String, nullable=False)
    id_funcionario = Column(Integer, nullable=True)
