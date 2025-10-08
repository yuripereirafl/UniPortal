# routes/metas.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from app.database import get_db
from app.dependencies import get_current_user
from app.models.metas_colaboradores import MetaColaborador
from app.schemas.metas import MetaColaborador as MetaColaboradorSchema

router = APIRouter(
    prefix="/metas",  # Prefixo corrigido para /metas
    tags=["Metas"]
)

@router.get("/minha-meta", response_model=List[MetaColaboradorSchema])
def get_minha_meta(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retorna as metas do funcionário associado ao usuário logado.
    """
    print(f"--- [ROTA METAS] Buscando metas para usuário: {current_user.username} (id_funcionario: {current_user.id_funcionario}) ---")
    
    if not current_user.id_funcionario:
        print(f"--- [ROTA METAS] Usuário {current_user.username} não tem funcionário associado ---")
        raise HTTPException(status_code=404, detail="Usuário não tem funcionário associado")
    
    # Buscar funcionário pelo ID
    from app.models.funcionario import Funcionario
    funcionario = db.query(Funcionario).filter(Funcionario.id == current_user.id_funcionario).first()
    
    if not funcionario:
        print(f"--- [ROTA METAS] Funcionário com ID {current_user.id_funcionario} não encontrado ---")
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    
    if not funcionario.cpf:
        print(f"--- [ROTA METAS] Funcionário {funcionario.nome} não possui CPF cadastrado ---")
        raise HTTPException(status_code=404, detail="Funcionário não possui CPF cadastrado")
    
    # Buscar metas do funcionário pelo CPF
    metas = db.query(MetaColaborador).filter(MetaColaborador.cpf == funcionario.cpf).all()
    
    if not metas:
        print(f"--- [ROTA METAS] Nenhuma meta encontrada para o funcionário {funcionario.nome} (CPF: {funcionario.cpf}) ---")
        raise HTTPException(status_code=404, detail="Nenhuma meta encontrada para este funcionário")
    
    print(f"--- [ROTA METAS] Encontradas {len(metas)} metas para {funcionario.nome}. Retornando 200 OK. ---")
    return metas


@router.get("/colaboradores-com-metas")
def get_colaboradores_com_metas(db: Session = Depends(get_db)):
    """
    Retorna lista de todos os colaboradores que possuem metas cadastradas.
    """
    print("--- [ROTA METAS] Buscando todos os colaboradores com metas (OTIMIZADO) ---")
    
    # Busca otimizada: uma única query com window function para pegar o registro mais recente por id_eyal
    from sqlalchemy import func, and_
    from sqlalchemy.orm import aliased
    
    # Subquery para encontrar o mes_ref mais recente para cada id_eyal
    subq = db.query(
        MetaColaborador.id_eyal,
        func.max(MetaColaborador.mes_ref).label('max_mes_ref')
    ).filter(
        MetaColaborador.id_eyal.isnot(None)
    ).group_by(MetaColaborador.id_eyal).subquery()
    
    # Query principal que junta com a subquery para pegar apenas os registros mais recentes
    colaboradores_query = db.query(MetaColaborador).join(
        subq,
        and_(
            MetaColaborador.id_eyal == subq.c.id_eyal,
            MetaColaborador.mes_ref == subq.c.max_mes_ref
        )
    ).all()
    
    print(f"--- [ROTA METAS] Processados {len(colaboradores_query)} colaboradores únicos (OTIMIZADO) ---")
    
    # Processa os resultados
    resultado = []
    for meta in colaboradores_query:
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
    
    print(f"--- [ROTA METAS] Processados {len(resultado)} colaboradores únicos (OTIMIZADO) ---")
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
