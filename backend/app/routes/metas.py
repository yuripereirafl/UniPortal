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

@router.get("/colaboradores-com-metas")
def get_colaboradores_com_metas(db: Session = Depends(get_db)):
    """
    Retorna lista de todos os colaboradores que possuem metas cadastradas.
    """
    print("--- [ROTA METAS] Buscando todos os colaboradores com metas ---")
    
    # Buscar colaboradores distintos que têm metas usando uma abordagem diferente
    # Primeiro, vamos buscar todos os id_eyal únicos
    ids_eyal_unicos = db.query(MetaColaborador.id_eyal)\
        .filter(MetaColaborador.id_eyal.isnot(None))\
        .distinct()\
        .all()
    
    print(f"--- [ROTA METAS] Encontrados {len(ids_eyal_unicos)} id_eyal únicos ---")
    
    # Agora buscar um registro para cada id_eyal único (o mais recente)
    resultado = []
    colaboradores_processados = set()  # Para evitar duplicatas
    
    for (id_eyal,) in ids_eyal_unicos:
        # Buscar o registro mais recente para este id_eyal
        meta = db.query(MetaColaborador)\
            .filter(MetaColaborador.id_eyal == id_eyal)\
            .order_by(MetaColaborador.mes_ref.desc())\
            .first()
        
        if meta and meta.cpf not in colaboradores_processados:
            colaborador = {
                "id": meta.cpf,  # Usando CPF como ID
                "cpf": meta.cpf,
                "nome": meta.nome,
                "cargo": meta.cargo,
                "unidade": meta.unidade,
                "equipe": meta.equipe,
                "lider_direto": meta.lider_direto,
                "nivel": meta.nivel,
                "funcao": meta.funcao,
                "meta_total": meta.meta_final,
                "meta_diaria": meta.meta_diaria,
                "dias_trabalhados": meta.dias_trabalhados,
                "dias_de_falta": meta.dias_de_falta,
                "mes_ref": meta.mes_ref,
                "id_eyal": meta.id_eyal
            }
            
            # Log específico para debug de dados vazios
            if not meta.cargo or not meta.unidade:
                print(f"--- [DEBUG] Colaborador {meta.nome} (CPF: {meta.cpf}) tem dados incompletos:")
                print(f"    Cargo: '{meta.cargo}' | Unidade: '{meta.unidade}' | Equipe: '{meta.equipe}'")
            
            resultado.append(colaborador)
            colaboradores_processados.add(meta.cpf)
    
    print(f"--- [ROTA METAS] Processados {len(resultado)} colaboradores únicos ---")
    return resultado


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
