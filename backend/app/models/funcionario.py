from app.models.cargo import Cargo
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.grupo_email import GrupoEmail


funcionario_setor = Table(
    'funcionario_setor', Base.metadata,
    Column('funcionario_id', Integer, ForeignKey('funcionarios.id')),
    Column('setor_id', Integer, ForeignKey('setores.id'))
)

funcionario_sistema = Table(
    'funcionario_sistema', Base.metadata,
    Column('funcionario_id', Integer, ForeignKey('funcionarios.id')),
    Column('sistema_id', Integer, ForeignKey('sistemas.id'))
)

funcionario_grupo_email = Table(
    'funcionario_grupo_email', Base.metadata,
    Column('funcionario_id', Integer, ForeignKey('funcionarios.id')),
    Column('grupo_email_id', Integer, ForeignKey('grupos_email.id'))
)


from app.models.grupo_pasta import funcionario_grupo_pasta

class Funcionario(Base):
    __tablename__ = 'funcionarios'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    sobrenome = Column(String, nullable=False)
    celular = Column(String, nullable=True)
    email = Column(String, nullable=False)
    equipe = Column(String, nullable=True)
    data_admissao = Column(String, nullable=True)
    data_rescisao = Column(String, nullable=True)
    data_afastamento = Column(String, nullable=True)
    data_retorno = Column(String, nullable=True)
    cpf = Column(String, unique=True)
    data_inativado = Column(String, nullable=True)
    tipo_contrato = Column(String, nullable=True)
    setores = relationship("Setor", secondary=funcionario_setor, backref="funcionarios")
    sistemas = relationship("Sistema", secondary=funcionario_sistema, backref="funcionarios")
    grupos_email = relationship("GrupoEmail", secondary=funcionario_grupo_email, backref="funcionarios")
    grupos_pasta = relationship("GrupoPasta", secondary=funcionario_grupo_pasta, back_populates="funcionarios")
