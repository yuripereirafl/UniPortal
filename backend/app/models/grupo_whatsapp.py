from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class GrupoWhatsapp(Base):
    __tablename__ = "grupos_whtss"
    __table_args__ = {'schema': 'rh_homologacao'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False, unique=True)
    descricao = Column(String(255))

    # Relacionamento many-to-many com funcionários
    funcionarios = relationship(
        "Funcionario",
        secondary="rh_homologacao.funcionario_grupo_whtss",
        back_populates="grupos_whatsapp"
    )

    def __repr__(self):
        return f"<GrupoWhatsapp(id={self.id}, nome='{self.nome}')>"
