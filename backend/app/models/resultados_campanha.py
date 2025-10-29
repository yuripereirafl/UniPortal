"""
Model para a tabela resultados_campanha
Armazena os valores finais de comissão já calculados por colaborador
"""
from sqlalchemy import Column, Date, String, Numeric, PrimaryKeyConstraint, Text
from app.models.base import Base


class ResultadoCampanha(Base):
    """
    Tabela que contém os valores FINAIS de comissão já calculados

    Esta tabela substitui o cálculo manual procedimento por procedimento.
    Contém os valores de comissão já processados e prontos para serem exibidos.
    """
    __tablename__ = "resultados_campanha"
    __table_args__ = (
        PrimaryKeyConstraint('mes_ref', 'id_eyal'),
        {'schema': 'rh_homologacao'}
    )

    mes_ref = Column(Date, nullable=False, primary_key=True)
    id_eyal = Column(String(255), nullable=False, primary_key=True)
    nome = Column(Text)
    cargo = Column(String(255))
    meta_final = Column(Numeric(18, 4))
    valor_a_pagar = Column(Numeric(18, 4))  # Valor da comissão de campanhas

    def __repr__(self):
        return f"<ResultadoCampanha(mes_ref={self.mes_ref}, id_eyal={self.id_eyal}, nome={self.nome}, valor_a_pagar={self.valor_a_pagar})>"