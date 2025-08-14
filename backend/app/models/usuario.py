from sqlalchemy import Column, Integer, String
from ..database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "rh_homologacao"}
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashsenha = Column(String, nullable=False)
