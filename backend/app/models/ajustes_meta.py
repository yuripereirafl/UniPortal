"""
Modelo para solicitações de troca/encaixe de procedimentos entre colaboradores
Baseado em solicitações reais por e-mail de coordenadores
"""

from sqlalchemy import Column, String, Float, Date, Integer, Boolean, Text, DateTime
from datetime import datetime
from app.models.base import Base


class SolicitacaoTroca(Base):
    """
    Tabela de solicitações de troca de procedimento entre colaboradores
    
    Fluxo:
    1. Coordenador solicita troca via e-mail
    2. Sistema registra solicitação
    3. Coordenador de origem aprova
    4. Ajuste é aplicado automaticamente na meta
    
    Exemplo:
    - SAI DO COLABORADOR: Ramon
    - ENTRA PARA O COLABORADOR: Andressa de Lima
    - VALOR: R$ 65,00
    - COD_PACIENTE: 309020
    """
    __tablename__ = 'solicitacoes_troca'
    __table_args__ = {'schema': 'rh_homologacao'}
    
    # Identificação
    id = Column(Integer, primary_key=True, autoincrement=True)
    mes_ref = Column(Date, nullable=False, index=True, comment="Mês de referência da solicitação")
    data_solicitacao = Column(DateTime, default=datetime.now, comment="Data/hora da solicitação")
    
    # Solicitante (Coordenador que pede)
    coordenador_solicitante = Column(String(255), nullable=False, comment="Nome do coordenador que solicita")
    email_solicitante = Column(String(255), comment="E-mail do solicitante")
    
    # Dados do procedimento
    cod_paciente = Column(String(50), comment="Código do paciente/agendamento")
    descricao_procedimento = Column(Text, comment="Descrição do procedimento")
    valor_procedimento = Column(Float, nullable=False, comment="Valor do procedimento")
    
    # Origem (SAI DO COLABORADOR)
    id_eyal_origem = Column(String(50), nullable=False, index=True, comment="ID do colaborador que CEDE")
    nome_origem = Column(String(255), nullable=False, comment="Nome do colaborador de origem")
    unidade_origem = Column(String(100), comment="Unidade do colaborador origem")
    coordenador_origem = Column(String(255), comment="Coordenador da unidade de origem")
    
    # Destino (ENTRA PARA O COLABORADOR)
    id_eyal_destino = Column(String(50), nullable=False, index=True, comment="ID do colaborador que RECEBE")
    nome_destino = Column(String(255), nullable=False, comment="Nome do colaborador de destino")
    unidade_destino = Column(String(100), comment="Unidade do colaborador destino")
    coordenador_destino = Column(String(255), comment="Coordenador da unidade de destino")
    
    # Tipo de solicitação
    tipo_solicitacao = Column(String(50), nullable=False, comment="TROCA_ENCAIXE, TRANSFERENCIA, CAMPANHA")
    motivo = Column(Text, comment="Motivo da troca")
    
    # Status e Aprovações
    status = Column(String(50), default='PENDENTE', comment="PENDENTE, APROVADA, REJEITADA, APLICADA")
    data_aprovacao_origem = Column(DateTime, comment="Data de aprovação do coordenador origem")
    aprovado_por_origem = Column(String(255), comment="Quem aprovou na origem")
    observacao_aprovacao = Column(Text, comment="Observação da aprovação")
    data_aplicacao = Column(DateTime, comment="Data em que o ajuste foi aplicado na meta")
    
    # Controle
    ativo = Column(Boolean, default=True, comment="Se a solicitação está ativa")
    criado_por = Column(String(100), comment="Usuário que criou a solicitação")
    
    # Rastreabilidade
    email_original = Column(Text, comment="Corpo do e-mail original (para auditoria)")
    ip_solicitante = Column(String(50), comment="IP de onde veio a solicitação")
    
    def __repr__(self):
        return f"<SolicitacaoTroca(origem={self.nome_origem}, destino={self.nome_destino}, valor={self.valor_procedimento}, status={self.status})>"
