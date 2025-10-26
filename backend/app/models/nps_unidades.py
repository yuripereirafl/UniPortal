from sqlalchemy import Column, Integer, String, Date
from app.models.base import Base

class NpsUnidades(Base):
    """
    Modelo para a tabela rh_homologacao.nps_unidades.

    Armazena dados agregados de NPS por unidade de pagamento,
    incluindo total de respondentes, promotores, detratores e neutros.
    """
    __tablename__ = 'nps_unidades'
    __table_args__ = {'schema': 'rh_homologacao'}

    mes_ref = Column(Date, primary_key=True, nullable=False)
    unidade_pagamento = Column(String(255), primary_key=True, nullable=False)
    cod_usuario = Column(Integer, primary_key=True, nullable=False)
    nome_atendeu = Column(String(255))
    total_respondentes = Column(Integer)
    total_promotores = Column(Integer)
    total_detratores = Column(Integer)
    total_neutros = Column(Integer)

    def calcular_nps(self) -> float:
        """
        Calcula o NPS baseado nos totais de promotores e detratores.

        Fórmula: NPS = ((Promotores - Detratores) / Total Respondentes) * 100

        Returns:
            float: Valor do NPS entre -100 e 100, ou 0.0 se não houver respondentes
        """
        if not self.total_respondentes or self.total_respondentes == 0:
            return 0.0

        promotores = self.total_promotores or 0
        detratores = self.total_detratores or 0

        nps = ((promotores - detratores) / self.total_respondentes) * 100
        return round(nps, 2)
