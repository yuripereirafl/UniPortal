"""
Modelo para a tabela basecampanhas - dados de vendas de campanhas
Fonte: rh_homologacao.basecampanhas
"""

from sqlalchemy import Column, String, TIMESTAMP, DECIMAL, Date, PrimaryKeyConstraint
from app.models.base import Base


class BaseCampanhas(Base):
    """
    Tabela com dados de vendas/agendamentos de campanhas
    
    Contém informações sobre:
    - Vendas de exames (Odonto, Check-up, BabyClick, etc)
    - Agendamentos realizados
    - Usuário que realizou o agendamento
    - Valores dos procedimentos
    """
    
    __tablename__ = "basecampanhas"
    __table_args__ = {"schema": "rh_homologacao"}
    
    # Campos da tabela
    mes = Column(Date, nullable=True, comment="Mês de referência")
    data_agenda = Column(TIMESTAMP, nullable=True, comment="Data e hora do agendamento")
    usuario_agendo = Column(String(100), nullable=True, comment="Nome do usuário que fez o agendamento")
    cod_usuario = Column(String(50), nullable=True, comment="Código do usuário (ID Eyal)")
    nome_exame_ajustado = Column(String(255), nullable=True, comment="Nome do exame ajustado")
    grupo_exames = Column(String(100), nullable=True, comment="Grupo: CHECK UP, ODONTO, BabyClick, etc")
    unidade = Column(String(50), nullable=True, comment="Unidade: OPERADOR, SITE, WHATSAPP")
    cod_paciente = Column(String(20), nullable=False, comment="Código do paciente")
    valor_original_proc = Column(DECIMAL(12, 4), nullable=True, comment="Valor original do procedimento")
    cod_agenda = Column(String(50), nullable=False, comment="Código da agenda (PK)")
    cod_exame = Column(String(50), nullable=False, comment="Código do exame (PK)")
    abrev_exame = Column(String(255), nullable=True, comment="Abreviação do exame")
    descricao_exame = Column(String, nullable=True, comment="Descrição completa do exame")
    data_carga = Column(Date, nullable=False, comment="Data de carga dos dados (PK)")
    
    # Chave primária composta
    __table_args__ = (
        PrimaryKeyConstraint('cod_agenda', 'cod_exame', 'data_carga'),
        {"schema": "rh_homologacao"}
    )
    
    def __repr__(self):
        return (
            f"<BaseCampanhas("
            f"usuario={self.usuario_agendo}, "
            f"grupo={self.grupo_exames}, "
            f"mes={self.mes}, "
            f"valor={self.valor_original_proc}"
            f")>"
        )
