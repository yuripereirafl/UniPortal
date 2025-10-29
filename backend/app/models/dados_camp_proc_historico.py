"""
Model para a tabela dados_camp_proc_historico
Armazena os valores de comissão por procedimento/exame para cada cargo
"""
from sqlalchemy import Column, DateTime, BigInteger, Text, Float, PrimaryKeyConstraint
from app.models.base import Base


class DadosCampProcHistorico(Base):
    """
    Tabela que contém os valores de comissão por procedimento/exame
    
    Exemplo de uso:
    - CHECK-UP CARDIO: valor R$ 4,00
        - Operadores: R$ 3,00 (75%)
        - Gerente: R$ 0,25 (6.25%)
        - Coordenador: R$ 0,35 (8.75%)
        - Supervisor: R$ 0,40 (10%)
    """
    __tablename__ = "dados_camp_proc_historico"
    __table_args__ = (
        PrimaryKeyConstraint('mes_ref', 'cod_exame'),
        {'schema': 'rh_homologacao'}
    )

    mes_ref = Column(DateTime, nullable=False, primary_key=True)
    cod_exame = Column(BigInteger, nullable=False, primary_key=True)
    descricao = Column(Text)
    valor = Column(Float)  # Valor total do procedimento
    abrev = Column(Text)  # Abreviação (ex: CARDIO, HOMEM, 107 - ODONTO)
    grupo = Column(Text)  # Grupo (ex: CHECK UP, ODONTO, BabyClick)
    
    # Valores de comissão por cargo
    operadores = Column(Float)  # Comissão para atendentes/operadores
    gerente = Column(Float)     # Comissão para gerente
    coord = Column(Float)       # Comissão para coordenador
    super = Column(Float)       # Comissão para supervisor

    def __repr__(self):
        return f"<DadosCampProcHistorico(mes_ref={self.mes_ref}, cod_exame={self.cod_exame}, descricao={self.descricao}, valor={self.valor})>"
    
    def get_comissao_por_cargo(self, cargo: str) -> float:
        """
        Retorna o valor de comissão apropriado baseado no cargo
        
        Args:
            cargo: Nome do cargo (ex: "ATENDENTE", "SUPERVISOR DE ATENDIMENTO", "COORDENADOR(A)")
            
        Returns:
            float: Valor de comissão para o cargo (0.0 se não encontrado)
        """
        cargo_lower = cargo.lower()
        
        if any(c in cargo_lower for c in ['atendente', 'estagiário', 'operador']):
            return self.operadores or 0.0
        elif 'supervisor' in cargo_lower or 'monitor' in cargo_lower:
            return self.super or 0.0
        elif 'coordenador' in cargo_lower:
            return self.coord or 0.0
        elif 'gerente' in cargo_lower:
            return self.gerente or 0.0
        
        # Default: operador
        return self.operadores or 0.0
