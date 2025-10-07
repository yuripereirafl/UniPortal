from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, date

from app.database import get_db
from app.models.metas_unidades import MetaUnidade
from app.models.metas_colaboradores import MetaColaborador
from app.models.realizado_colaboradores import RealizadoColaborador
from app.schemas.metas_unidades import (
    MetaUnidadeResponse, 
    MetaUnidadeCreate, 
    MetaUnidadeUpdate,
    DashboardUnidadeResponse,
    DashboardGeralResponse,
    UnidadeResponse,
    ResumoGeralResponse
)

router = APIRouter(prefix="/unidades", tags=["Metas das Unidades"])

@router.get("/", response_model=List[MetaUnidadeResponse])
def listar_metas_unidades(
    unidade: Optional[str] = None,
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todas as metas das unidades com filtros opcionais"""
    query = db.query(MetaUnidade).filter(MetaUnidade.ativo == 'S')
    
    if unidade:
        query = query.filter(MetaUnidade.unidade.ilike(f"%{unidade}%"))
    
    if mes_ref:
        query = query.filter(MetaUnidade.mes_ref == mes_ref)
    
    return query.order_by(MetaUnidade.mes_ref.desc(), MetaUnidade.unidade).all()

@router.get("/dashboard", response_model=DashboardGeralResponse)
def dashboard_geral(
    mes_ref: Optional[str] = Query(None, description="Mês de referência (YYYY-MM)"),
    db: Session = Depends(get_db)
):
    """
    Retorna dados consolidados do dashboard para todas as unidades.
    Inclui resumo geral e dados por unidade.
    """
    print("--- [DASHBOARD GERAL] Buscando dados de todas as unidades ---")
    
    # Se não foi fornecido mes_ref, usar o mês atual
    if not mes_ref:
        from datetime import datetime
        mes_ref = datetime.now().strftime("%Y-%m")
    
    print(f"--- [DASHBOARD GERAL] Mês de referência: {mes_ref} ---")
    
    # Buscar todas as metas das unidades
    query = db.query(MetaUnidade)
    if mes_ref:
        query = query.filter(MetaUnidade.mes_ref == mes_ref)
    
    metas_unidades = query.order_by(MetaUnidade.unidade).all()
    
    print(f"--- [DASHBOARD GERAL] Encontradas {len(metas_unidades)} unidades ---")
    
    if not metas_unidades:
        # Retornar dados vazios se não há dados
        return DashboardGeralResponse(
            unidades=[],
            resumo=ResumoGeralResponse(
                total_unidades=0,
                meta_total=0,
                realizado_total=0,
                percentual_medio=0
            )
        )
    
    # Calcular dados por unidade
    unidades_data = []
    meta_total_geral = 0
    realizado_total_geral = 0
    
    for meta_unidade in metas_unidades:
        # Para cada unidade, calcular percentual
        percentual = (meta_unidade.realizado / meta_unidade.meta * 100) if meta_unidade.meta > 0 else 0
        diferenca = meta_unidade.realizado - meta_unidade.meta
        
        unidade_data = UnidadeResponse(
            id=meta_unidade.id,
            unidade=meta_unidade.unidade,
            mes=meta_unidade.mes_ref,
            meta=meta_unidade.meta,
            realizado=meta_unidade.realizado,
            diferenca=diferenca,
            percentual_atingimento=percentual
        )
        
        unidades_data.append(unidade_data)
        meta_total_geral += meta_unidade.meta
        realizado_total_geral += meta_unidade.realizado
    
    # Calcular percentual médio
    percentual_medio = (realizado_total_geral / meta_total_geral * 100) if meta_total_geral > 0 else 0
    
    # Criar resumo geral
    resumo = ResumoGeralResponse(
        total_unidades=len(metas_unidades),
        meta_total=meta_total_geral,
        realizado_total=realizado_total_geral,
        percentual_medio=percentual_medio
    )
    
    print(f"--- [DASHBOARD GERAL] Resumo: {len(metas_unidades)} unidades, Meta: {meta_total_geral}, Realizado: {realizado_total_geral} ---")
    
    return DashboardGeralResponse(
        unidades=unidades_data,
        resumo=resumo
    )

@router.get("/dashboard/{unidade}", response_model=DashboardUnidadeResponse)
def dashboard_unidade(
    unidade: str,
    mes_ref: Optional[str] = Query(None, description="Mês de referência (YYYY-MM)"),
    db: Session = Depends(get_db)
):
    """
    Retorna dados consolidados do dashboard para uma unidade específica.
    Inclui metas, realizados e indicadores calculados.
    """
    print(f"--- [DASHBOARD UNIDADE] Buscando dados para: {unidade} ---")
    
    # Se não foi fornecido mes_ref, usar o mês atual
    if not mes_ref:
        mes_ref = datetime.now().strftime("%Y-%m")
    
    print(f"--- [DASHBOARD UNIDADE] Mês de referência: {mes_ref} ---")
    
    # 1. Buscar meta da unidade
    meta_unidade = db.query(MetaUnidade).filter(
        and_(
            MetaUnidade.unidade.ilike(f"%{unidade}%"),
            MetaUnidade.mes_ref == mes_ref,
            MetaUnidade.ativo == 'S'
        )
    ).first()
    
    if not meta_unidade:
        raise HTTPException(
            status_code=404, 
            detail=f"Meta não encontrada para a unidade '{unidade}' no mês '{mes_ref}'"
        )
    
    print(f"--- [DASHBOARD UNIDADE] Meta encontrada: {meta_unidade.meta_total} ---")
    
    # 2. Buscar colaboradores da unidade
    colaboradores_unidade = db.query(MetaColaborador).filter(
        and_(
            MetaColaborador.unidade.ilike(f"%{unidade}%"),
            MetaColaborador.mes_ref == mes_ref
        )
    ).all()
    
    total_colaboradores = len(colaboradores_unidade)
    colaboradores_ativos = len([c for c in colaboradores_unidade if c.meta_final and c.meta_final > 0])
    
    print(f"--- [DASHBOARD UNIDADE] Colaboradores: {total_colaboradores} total, {colaboradores_ativos} ativos ---")
    
    # 3. Buscar dados realizados da unidade
    # Somar todos os realizados dos colaboradores desta unidade
    ids_eyal_unidade = [int(c.id_eyal) for c in colaboradores_unidade if c.id_eyal]
    
    if not ids_eyal_unidade:
        # Se não há IDs válidos, retornar dados zerados
        realizado_total = 0
        realizado_por_categoria = {}
    else:
        # Buscar realizado total
        realizado_query = db.query(
            func.sum(RealizadoColaborador.total_realizado).label('total')
        ).filter(
            RealizadoColaborador.id_eyal.in_(ids_eyal_unidade)
        ).first()
        
        realizado_total = float(realizado_query.total) if realizado_query.total else 0
        
        # Buscar realizado por categoria
        realizado_categorias = db.query(
            RealizadoColaborador.tipo_grupo,
            func.sum(RealizadoColaborador.total_realizado).label('total')
        ).filter(
            RealizadoColaborador.id_eyal.in_(ids_eyal_unidade)
        ).group_by(RealizadoColaborador.tipo_grupo).all()
        
        realizado_por_categoria = {cat.tipo_grupo: float(cat.total) for cat in realizado_categorias}
    
    print(f"--- [DASHBOARD UNIDADE] Realizado total: {realizado_total} ---")
    print(f"--- [DASHBOARD UNIDADE] Por categoria: {realizado_por_categoria} ---")
    
    # 4. Calcular indicadores
    percentual_total = (realizado_total / meta_unidade.meta_total * 100) if meta_unidade.meta_total > 0 else 0
    
    def calcular_percentual(realizado, meta):
        return (realizado / meta * 100) if meta and meta > 0 else 0
    
    # Mapear categorias (ajuste conforme necessário)
    realizado_odonto = realizado_por_categoria.get('Odonto', 0)
    realizado_checkup = realizado_por_categoria.get('Check-up', 0)
    realizado_dr_central = realizado_por_categoria.get('Dr. Central', 0)
    realizado_babyclick = realizado_por_categoria.get('BabyClick', 0)
    
    # 5. Montar resposta
    dashboard_data = DashboardUnidadeResponse(
        unidade=meta_unidade.unidade,
        mes_ref=meta_unidade.mes_ref,
        
        # Metas
        meta_total=meta_unidade.meta_total or 0,
        meta_odonto=meta_unidade.meta_odonto,
        meta_checkup=meta_unidade.meta_checkup,
        meta_dr_central=meta_unidade.meta_dr_central,
        meta_babyclick=meta_unidade.meta_babyclick,
        
        # Realizados
        realizado_total=realizado_total,
        realizado_odonto=realizado_odonto,
        realizado_checkup=realizado_checkup,
        realizado_dr_central=realizado_dr_central,
        realizado_babyclick=realizado_babyclick,
        
        # Percentuais
        percentual_total=round(percentual_total, 1),
        percentual_odonto=round(calcular_percentual(realizado_odonto, meta_unidade.meta_odonto), 1) if meta_unidade.meta_odonto else None,
        percentual_checkup=round(calcular_percentual(realizado_checkup, meta_unidade.meta_checkup), 1) if meta_unidade.meta_checkup else None,
        percentual_dr_central=round(calcular_percentual(realizado_dr_central, meta_unidade.meta_dr_central), 1) if meta_unidade.meta_dr_central else None,
        percentual_babyclick=round(calcular_percentual(realizado_babyclick, meta_unidade.meta_babyclick), 1) if meta_unidade.meta_babyclick else None,
        
        # Informações
        total_colaboradores=total_colaboradores,
        colaboradores_ativos=colaboradores_ativos
    )
    
    print(f"--- [DASHBOARD UNIDADE] Dashboard montado com sucesso ---")
    return dashboard_data

@router.get("/lista-unidades", response_model=List[str])
def listar_unidades_disponiveis(db: Session = Depends(get_db)):
    """Lista todas as unidades que têm metas cadastradas"""
    unidades = db.query(MetaUnidade.unidade).filter(
        MetaUnidade.ativo == 'S'
    ).distinct().all()
    
    return [unidade[0] for unidade in unidades]

@router.post("/", response_model=MetaUnidadeResponse)
def criar_meta_unidade(meta: MetaUnidadeCreate, db: Session = Depends(get_db)):
    """Cria uma nova meta para uma unidade"""
    
    # Verificar se já existe meta para esta unidade/mês
    meta_existente = db.query(MetaUnidade).filter(
        and_(
            MetaUnidade.unidade == meta.unidade,
            MetaUnidade.mes_ref == meta.mes_ref,
            MetaUnidade.ativo == 'S'
        )
    ).first()
    
    if meta_existente:
        raise HTTPException(
            status_code=400,
            detail=f"Já existe uma meta para a unidade '{meta.unidade}' no mês '{meta.mes_ref}'"
        )
    
    nova_meta = MetaUnidade(
        **meta.dict(),
        data_criacao=date.today(),
        data_atualizacao=date.today(),
        ativo='S'
    )
    
    db.add(nova_meta)
    db.commit()
    db.refresh(nova_meta)
    
    return nova_meta

@router.put("/{meta_id}", response_model=MetaUnidadeResponse)
def atualizar_meta_unidade(
    meta_id: int, 
    meta_update: MetaUnidadeUpdate, 
    db: Session = Depends(get_db)
):
    """Atualiza uma meta existente"""
    
    meta = db.query(MetaUnidade).filter(MetaUnidade.id == meta_id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    
    # Atualizar campos fornecidos
    for field, value in meta_update.dict(exclude_unset=True).items():
        if value is not None:
            setattr(meta, field, value)
    
    meta.data_atualizacao = date.today()
    
    db.commit()
    db.refresh(meta)
    
    return meta

@router.delete("/{meta_id}")
def inativar_meta_unidade(meta_id: int, db: Session = Depends(get_db)):
    """Inativa uma meta (soft delete)"""
    
    meta = db.query(MetaUnidade).filter(MetaUnidade.id == meta_id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    
    meta.ativo = 'N'
    meta.data_atualizacao = date.today()
    
    db.commit()
    
    return {"message": "Meta inativada com sucesso"}