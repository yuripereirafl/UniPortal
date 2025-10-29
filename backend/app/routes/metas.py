# routes/metas.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from typing import List, Optional
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.funcionario import Funcionario
# Importações corrigidas para usar o model e schema de METAS
from app.models.metas_colaboradores import MetaColaborador
from app.schemas.metas import MetaColaborador as MetaColaboradorSchema

router = APIRouter(
    prefix="/metas",  # Prefixo corrigido para /metas
    tags=["Metas"]
)

@router.get("/meses-disponiveis")
def get_meses_disponiveis(db: Session = Depends(get_db)):
    """
    Retorna lista de meses disponíveis para filtrar metas e realizado,
    ordenados do mais recente para o mais antigo.
    
    Returns:
        {"meses": ["2025-10-01", "2025-09-01", ...]}
    """
    print("--- [ROTA METAS] Buscando meses disponíveis ---")
    
    # Buscar meses distintos das metas, ordenados DESC
    meses = db.query(MetaColaborador.mes_ref)\
        .distinct()\
        .order_by(desc(MetaColaborador.mes_ref))\
        .all()
    
    # Converter para lista de strings
    lista_meses = [str(mes.mes_ref) for mes in meses]
    
    print(f"--- [ROTA METAS] Encontrados {len(lista_meses)} meses: {lista_meses} ---")
    
    return {"meses": lista_meses}

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
    
    # Ordenar alfabeticamente por nome
    resultado_ordenado = sorted(resultado, key=lambda x: x['nome'].upper() if x['nome'] else '')
    
    print(f"--- [ROTA METAS] Processados {len(resultado_ordenado)} colaboradores únicos (ordenados alfabeticamente) ---")
    return resultado_ordenado


@router.get("/minha-meta", response_model=List[MetaColaboradorSchema])
def get_minha_meta(
    mes_ref: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna as metas do usuário logado com base no CPF do funcionário associado.
    
    Args:
        mes_ref: Mês de referência (formato 'YYYY-MM-DD'). Se não fornecido, retorna todos os meses ordenados por mais recente.
    """
    try:
        print(f"--- [ROTA METAS] Buscando meta do usuário logado: {current_user.username} ---")
        print(f"--- [ROTA METAS] ID funcionário: {current_user.id_funcionario} ---")
        print(f"--- [ROTA METAS] Mês de referência: {mes_ref or 'Todos'} ---")
        
        # Verificar se o usuário tem id_funcionario
        if not current_user.id_funcionario:
            print(f"--- [ROTA METAS] Usuário {current_user.username} não tem id_funcionario definido ---")
            raise HTTPException(
                status_code=404, 
                detail="Usuário não está associado a um funcionário."
            )
        
        # Buscar o funcionário associado
        funcionario = db.query(Funcionario).filter(Funcionario.id == current_user.id_funcionario).first()
        
        if not funcionario:
            print(f"--- [ROTA METAS] Funcionário com ID {current_user.id_funcionario} não encontrado ---")
            raise HTTPException(
                status_code=404, 
                detail="Funcionário associado não encontrado no sistema."
            )
        
        cpf_funcionario = funcionario.cpf
        print(f"--- [ROTA METAS] CPF do funcionário associado: {cpf_funcionario} ---")
        
        # Construir query base
        query = db.query(MetaColaborador).filter(
            MetaColaborador.cpf == cpf_funcionario
        )
        
        # Se mes_ref foi especificado, filtrar por mês
        if mes_ref:
            query = query.filter(MetaColaborador.mes_ref == mes_ref)
            print(f"--- [ROTA METAS] Filtrando por mês: {mes_ref} ---")
        
        # Buscar metas do funcionário, ordenadas por mês mais recente
        metas = query.order_by(desc(MetaColaborador.mes_ref)).all()
        
        if not metas:
            mes_info = f" no mês {mes_ref}" if mes_ref else ""
            print(f"--- [ROTA METAS] Nenhuma meta encontrada para o CPF {cpf_funcionario}{mes_info} ---")
            raise HTTPException(
                status_code=404, 
                detail=f"Nenhuma meta encontrada para o funcionário associado ao seu usuário{mes_info}."
            )
        
        print(f"--- [ROTA METAS] Encontradas {len(metas)} metas para o CPF {cpf_funcionario} ---")
        return metas
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"--- [ROTA METAS] ERRO: {str(e)} ---")
        print(f"--- [ROTA METAS] Tipo do erro: {type(e).__name__} ---")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar metas: {str(e)}"
        )


@router.get("/colaborador/{identificador}", response_model=List[MetaColaboradorSchema])
def get_metas_colaborador(
    identificador: str, 
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retorna as metas de um colaborador com base no CPF ou id_eyal.
    
    Args:
        identificador: CPF ou ID Eyal do colaborador
        mes_ref: Mês de referência (formato 'YYYY-MM-DD'). Se não fornecido, retorna todos os meses ordenados.
    """
    print(f"--- [ROTA METAS] Procurando por identificador: {identificador} ---")
    print(f"--- [ROTA METAS] Mês de referência: {mes_ref or 'Todos'} ---")

    # Construir query base
    query = db.query(MetaColaborador).filter(
        or_(
            MetaColaborador.cpf == identificador,
            MetaColaborador.id_eyal == identificador
        )
    )
    
    # Se mes_ref foi especificado, filtrar por mês
    if mes_ref:
        query = query.filter(MetaColaborador.mes_ref == mes_ref)
        print(f"--- [ROTA METAS] Filtrando por mês: {mes_ref} ---")
    
    # Buscar metas ordenadas por mês mais recente
    metas = query.order_by(desc(MetaColaborador.mes_ref)).all()

    if not metas:
        mes_info = f" no mês {mes_ref}" if mes_ref else ""
        print(f"--- [ROTA METAS] Nenhuma meta encontrada para {identificador}{mes_info}. Retornando 404. ---")
        raise HTTPException(status_code=404, detail=f"Metas não encontradas para o colaborador informado{mes_info}.")

    print(f"--- [ROTA METAS] Encontradas {len(metas)} metas. Retornando 200 OK. ---")
    return metas
