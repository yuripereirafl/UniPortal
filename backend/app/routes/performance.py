from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db

# Importe os modelos das suas tabelas
from app.models.funcionario import Funcionario 
from app.models.meta import Meta # Supondo que você tenha um modelo Meta
from app.models.realizado_colaboradores import RealizadoColaborador

# Importe o novo schema de resposta
from app.schemas.performance import PerformanceColaborador, RealizadoItem

router = APIRouter(
    prefix="/performance",
    tags=["Performance"]
)

@router.get("/colaborador/{cpf}", response_model=PerformanceColaborador)
def get_performance_por_cpf(cpf: str, db: Session = Depends(get_db)):
    """
    Retorna os dados consolidados de performance (Funcionário + Meta + Realizado)
    de um colaborador a partir do seu CPF.
    """

    # 1. Faz o JOIN entre Funcionario e Meta para encontrar o id_eyal
    #    O .first() é usado aqui porque esperamos apenas um funcionário por CPF.
    funcionario_meta = db.query(
        Funcionario.nome,
        Funcionario.sobrenome,
        Funcionario.cpf,
        Meta.id_eyal,
        Meta.valor_meta_total # Supondo um campo de meta total na sua tabela Meta
    ).join(
        Meta, Funcionario.cpf == Meta.cpf
    ).filter(
        Funcionario.cpf == cpf
    ).first()

    if not funcionario_meta:
        raise HTTPException(status_code=404, detail="Funcionário ou meta não encontrado para o CPF fornecido.")

    # 2. Com o id_eyal, busca todos os registros de 'realizado'
    #    O .all() é usado aqui porque um colaborador pode ter vários registros.
    registros_realizado = db.query(RealizadoColaborador).filter(
        RealizadoColaborador.id_eyal == funcionario_meta.id_eyal
    ).all()
    
    # 3. Calcula a soma total dos valores realizados
    soma_realizado = sum(r.total_realizado for r in registros_realizado)

    # 4. Monta o objeto de resposta final usando o schema
    resposta = PerformanceColaborador(
        nome_completo=f"{funcionario_meta.nome} {funcionario_meta.sobrenome}",
        cpf=funcionario_meta.cpf,
        id_eyal=funcionario_meta.id_eyal,
        meta_total=funcionario_meta.valor_meta_total,
        realizados=[RealizadoItem.model_validate(r) for r in registros_realizado],
        soma_total_realizado=soma_realizado
    )

    return resposta