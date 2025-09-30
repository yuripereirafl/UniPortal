from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.realizado_colaboradores import RealizadoColaborador
from app.schemas.realizado import RealizadoColaborador as RealizadoSchema
from sqlalchemy import func


from pydantic import BaseModel
from typing import List

router = APIRouter(
    prefix="/realizado",
    tags=["Realizado"]
)

@router.get("/colaborador/{identificador}", response_model=List[RealizadoSchema])
def get_realizado_colaborador(identificador: int, db: Session = Depends(get_db)):
    """
    Retorna os dados realizados de um colaborador com base no id_eyal.
    """
    # A consulta já está correta para buscar todos os registros com .all()
    realizados = db.query(RealizadoColaborador).filter(
        RealizadoColaborador.id_eyal == identificador
    ).all()
    if not realizados:
        raise HTTPException(status_code=404, detail="Dados de 'realizado' não encontrados para o colaborador.")

    return realizados

# Nova rota para o resumo
@router.get("/colaborador/{identificador}/resumo")
def get_resumo_colaborador(identificador: int, db: Session = Depends(get_db)):
    """
    Retorna um resumo com os totais realizados de um colaborador,
    agrupados por tipo_grupo, e um total geral.
    """
    
    # Query que agrupa os resultados por 'tipo_grupo' e calcula a soma
    resumo_por_grupo = db.query(
        RealizadoColaborador.tipo_grupo,
        func.sum(RealizadoColaborador.total_realizado).label("total")
    ).filter(
        RealizadoColaborador.id_eyal == identificador
    ).group_by(
        RealizadoColaborador.tipo_grupo
    ).all()

    # Transforma o resultado em um dicionário mais amigável
    resumo_final = {item.tipo_grupo: item.total for item in resumo_por_grupo}
    
    # Calcula o total geral
    total_geral = sum(resumo_final.values())
    resumo_final["TOTAL_GERAL"] = total_geral

    if not resumo_final:
        raise HTTPException(status_code=404, detail="Dados não encontrados.")

    return resumo_final

# 1. Crie um novo Schema para a resposta da nova rota.
#    Isso define como será o JSON de saída.
class RealizadoUnidadeSchema(BaseModel):
    unidade: str
    total_realizado: float

    class Config:
        from_attributes = True # Permite que o Pydantic leia dados de objetos SQLAlchemy

# 2. Adicione a nova rota ao seu router existente.
@router.get("/unidade", response_model=List[RealizadoUnidadeSchema])
def get_realizado_por_unidade(db: Session = Depends(get_db)):
    """
    Retorna a soma do total realizado para todos os colaboradores,
    agrupado por unidade.
    """
    # A query com SQLAlchemy para agrupar por 'unidade' e somar 'total_realizado'
    # Removemos o filtro por 'id_eyal' para incluir todos os colaboradores.
    realizado_agrupado = db.query(
        RealizadoColaborador.unidade,
        func.sum(RealizadoColaborador.total_realizado).label("total_realizado")
    ).group_by(
        RealizadoColaborador.unidade
    ).order_by(
        RealizadoColaborador.unidade
    ).all()

    # Se a consulta não retornar nada, lança um erro 404
    if not realizado_agrupado:
        raise HTTPException(status_code=404, detail="Nenhum dado de realizado encontrado.")

    # Retorna a lista de resultados. O FastAPI fará a conversão para o formato JSON.
    return realizado_agrupado

@router.get("/unidade/{nome_unidade}", response_model=RealizadoUnidadeSchema)
def get_realizado_por_unidade_especifica(nome_unidade: str, db: Session = Depends(get_db)):
    """
    Retorna a SOMA do total realizado para todos os colaboradores
    de UMA unidade específica.
    """
    # 1. A query agora soma 'total_realizado' e filtra pela unidade.
    #    O .scalar() pega o resultado único da soma.
    soma_total = db.query(
        func.sum(RealizadoColaborador.total_realizado)
    ).filter(
        RealizadoColaborador.unidade == nome_unidade
    ).scalar()

    # 2. Se a unidade não existir ou não tiver registros, a soma será None.
    if soma_total is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Nenhum dado de 'realizado' encontrado para a unidade: {nome_unidade}"
        )

    # 3. Retorna um dicionário que corresponde ao schema 'RealizadoUnidadeSchema'.
    return {"unidade": nome_unidade, "total_realizado": soma_total}

# --- FIM DA ATUALIZAÇÃO ---