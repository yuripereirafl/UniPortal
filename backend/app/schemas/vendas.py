"""
Schemas para validação e resposta da API de vendas
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime


class VendasPorGrupo(BaseModel):
    """Dados agregados de vendas por grupo de exames"""
    grupo: str = Field(..., description="Grupo de exames: ODONTO, CHECK UP, BabyClick, etc")
    quantidade: int = Field(..., description="Quantidade de vendas do grupo")
    valor_total: float = Field(..., description="Valor total das vendas do grupo")
    
    model_config = ConfigDict(from_attributes=True)


class ResumoVendas(BaseModel):
    """Resumo das vendas de um colaborador"""
    cod_usuario: str = Field(..., description="Código do usuário (ID Eyal)")
    nome_usuario: str = Field(..., description="Nome do colaborador")
    mes_referencia: date = Field(..., description="Mês de referência das vendas")
    total_vendas: int = Field(..., description="Total de vendas realizadas")
    valor_total: float = Field(..., description="Valor total de todas as vendas")
    
    # Contadores por tipo (formato esperado pelo frontend)
    odonto: int = Field(default=0, description="Quantidade de vendas ODONTO")
    check_up: int = Field(default=0, description="Quantidade de vendas CHECK UP")
    baby_click: int = Field(default=0, description="Quantidade de vendas BabyClick")
    dr_central: int = Field(default=0, description="Quantidade de vendas DR CENTRAL")
    orcamentos: int = Field(default=0, description="Outros orçamentos")
    
    # Detalhamento por grupo
    vendas_por_grupo: List[VendasPorGrupo] = Field(default_factory=list, description="Vendas agrupadas por tipo")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat()
        }
    )


class DetalheVenda(BaseModel):
    """Detalhamento de uma venda específica"""
    mes: date = Field(..., description="Mês de referência")
    data_agenda: datetime = Field(..., description="Data do agendamento")
    cod_paciente: str = Field(..., description="Código do paciente")
    nome_exame: str = Field(..., description="Nome do exame")
    grupo_exames: str = Field(..., description="Grupo do exame")
    valor: float = Field(..., description="Valor do procedimento")
    unidade: str = Field(..., description="Unidade de atendimento")
    abrev_exame: Optional[str] = Field(None, description="Abreviação do exame")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v else 0.0
        }
    )


class VendasResponse(BaseModel):
    """Resposta completa da API de vendas"""
    success: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    resumo: Optional[ResumoVendas] = Field(None, description="Resumo das vendas")
    detalhes: List[DetalheVenda] = Field(default_factory=list, description="Lista detalhada de vendas")
    message: Optional[str] = Field(None, description="Mensagem adicional")
    
    model_config = ConfigDict(from_attributes=True)
