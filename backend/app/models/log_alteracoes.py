from sqlalchemy import Column, BigInteger, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.models.base import Base

class LogAlteracoes(Base):
    __tablename__ = "log_alteracoes"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id = Column(BigInteger, ForeignKey("usuarios.id"))
    tabela = Column(String(100), nullable=False)
    registro_id = Column(BigInteger, nullable=False)
    campo = Column(String(100), nullable=False)
    valor_antigo = Column(Text)
    valor_novo = Column(Text)
    data_alteracao = Column(TIMESTAMP, server_default=func.now(), nullable=False)