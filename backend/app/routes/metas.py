# routes/metas.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from app.database import get_db
# Importações corrigidas para usar o model e schema de METAS
from app.models.metas_colaboradores import MetaColaborador
from app.schemas.metas import MetaColaborador as MetaColaboradorSchema

router = APIRouter(
    prefix="/metas",  # Prefixo corrigido para /metas
    tags=["Metas"]
)

@router.get("/colaborador/{identificador}", response_model=List[MetaColaboradorSchema])
def get_metas_colaborador(identificador: str, db: Session = Depends(get_db)):
    """
    Retorna as metas de um colaborador com base no CPF ou id_eyal.
    """
    print(f"--- [ROTA METAS] Procurando por identificador: {identificador} ---")

    metas = db.query(MetaColaborador).filter(
        or_(
            MetaColaborador.cpf == identificador,
            MetaColaborador.id_eyal == identificador
        )
    ).all()

    if not metas:
        print(f"--- [ROTA METAS] Nenhuma meta encontrada para {identificador}. Retornando 404. ---")
        raise HTTPException(status_code=404, detail="Metas não encontradas para o colaborador informado.")

    print(f"--- [ROTA METAS] Encontradas {len(metas)} metas. Retornando 200 OK. ---")
    return metas
