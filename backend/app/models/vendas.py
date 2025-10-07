"""
Modelo SQLAlchemy para a tabela basecampanhas - vendas de colaboradores
"""

from sqlalchemy import Column, String, Date, DateTime, Numeric, PrimaryKeyConstraint
from ..database import Base


class BaseCampanhas(Base):
    """
    Tabela de vendas de colaboradores
    Armazena todos os agendamentos e vendas realizadas
    """
    __tablename__ = 'basecampanhas'
    __table_args__ = (
        PrimaryKeyConstraint('cod_agenda', 'cod_exame', 'data_carga'),
        {'schema': 'rh_homologacao'}
    )
    
    # Campos de referência temporal
    mes = Column(Date, nullable=False, comment="Mês de referência da venda")
    data_agenda = Column(DateTime, nullable=False, comment="Data do agendamento")
    data_carga = Column(Date, nullable=False, comment="Data de carga dos dados")
    
    # Dados do colaborador
    usuario_agendo = Column(String(100), comment="Nome do colaborador que fez a venda")
    cod_usuario = Column(String(50), comment="Código do colaborador (ID Eyal)")
    
    # Dados do exame/procedimento
    nome_exame_ajustado = Column(String(255), comment="Nome do exame/procedimento")
    grupo_exames = Column(String(100), comment="Grupo: ODONTO, CHECK UP, BabyClick")
    abrev_exame = Column(String(255), comment="Abreviação do exame (DR CENTRAL identificado aqui)")
    descricao_exame = Column(String, comment="Descrição completa do exame")
    
    # Dados da venda
    cod_paciente = Column(String(20), nullable=False, comment="Código do paciente")
    valor_original_proc = Column(Numeric(12, 4), comment="Valor do procedimento")
    unidade = Column(String(50), comment="Unidade: OPERADOR, SITE, WHATSAPP")
    
    # Chaves primárias compostas
    cod_agenda = Column(String(50), nullable=False, comment="Código da agenda (PK)")
    cod_exame = Column(String(50), nullable=False, comment="Código do exame (PK)")
    
    def __repr__(self):
        return f"<BaseCampanhas(usuario={self.usuario_agendo}, grupo={self.grupo_exames}, valor={self.valor_original_proc})>"
