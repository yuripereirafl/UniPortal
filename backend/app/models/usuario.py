from sqlalchemy import Column, Integer, String, BigInteger
from ..database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column("hashsenha", String, nullable=False)
    id_funcionario = Column(BigInteger, nullable=True)
