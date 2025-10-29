from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# Schema para um item de realizado (que você já tem)
class RealizadoItem(BaseModel):
    unidade: Optional[str] = None
    tipo_grupo: Optional[str] = None
    total_registros: Optional[int] = None
    total_realizado: Optional[float] = None

# Novo Schema para a resposta COMPLETA
class PerformanceColaborador(BaseModel):
    # Dados da tabela Funcionario
    nome_completo: str
    cpf: str
    
    # Dados da tabela Meta
    id_eyal: int
    meta_total: Optional[float] = None # Supondo que a meta tenha um valor total

    # Dados da tabela Realizado (pode ser uma lista)
    realizados: List[RealizadoItem] = []
    
    # Um campo calculado para facilitar
    soma_total_realizado: float = 0.0

    class Config:
        from_attributes = True