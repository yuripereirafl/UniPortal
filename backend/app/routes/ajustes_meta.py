"""
API para gerenciamento de ajustes de meta entre colaboradores
Equivalente às planilhas AJUSTES_R6 e AJUSTES_CAMPANHAS
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel

from app.dependencies import get_db
from app.models.ajustes_meta import AjusteMeta, AjusteADMDistribuido
from app.models.metas_colaboradores import MetaColaborador

router = APIRouter(
    prefix="/ajustes-meta",
    tags=["Ajustes de Meta"]
)


# ===== SCHEMAS =====

class AjusteMetaCreate(BaseModel):
    """Schema para criar um novo ajuste"""
    mes_ref: str  # Formato 'YYYY-MM-DD'
    tipo_ajuste: str  # 'R6', 'CAMPANHA', 'ADM_DISTRIBUIDO'
    motivo: Optional[str] = None
    
    id_eyal_origem: str
    id_eyal_destino: str
    
    valor_ajuste: float
    criterio: str  # 'PELA_UNIDADE' ou 'PELO_QUE_REALIZOU'
    observacao: Optional[str] = None


class AjusteMetaResponse(BaseModel):
    """Schema de resposta de ajuste"""
    id: int
    mes_ref: date
    tipo_ajuste: str
    motivo: Optional[str]
    
    nome_origem: str
    nome_destino: str
    valor_ajuste: float
    criterio: str
    
    ativo: bool
    
    class Config:
        from_attributes = True


class AjustesCalculadosResponse(BaseModel):
    """Resposta com ajustes calculados para um colaborador"""
    id_eyal: str
    nome: str
    mes_ref: str
    
    # Ajustes recebidos (valores que ENTRAM)
    ajustes_r6_recebidos: float
    ajustes_campanhas_recebidos: float
    ajustes_adm_recebidos: float
    
    # Ajustes cedidos (valores que SAEM)
    ajustes_r6_cedidos: float
    ajustes_campanhas_cedidos: float
    
    # Total líquido
    total_ajustes: float
    
    # Detalhamento
    detalhes: List[dict]


# ===== ENDPOINTS =====

@router.post("/criar", response_model=AjusteMetaResponse)
async def criar_ajuste(
    ajuste: AjusteMetaCreate,
    db: Session = Depends(get_db)
):
    """
    Cria um novo ajuste de meta entre colaboradores
    
    Exemplo:
    - Colaborador A (origem) cede R$ 5.000 para Colaborador B (destino)
    - Motivo: "Transferência de campanha Baby Click"
    """
    try:
        # Buscar nomes dos colaboradores
        mes_ref_date = datetime.strptime(ajuste.mes_ref, "%Y-%m-%d").date()
        
        origem = db.query(MetaColaborador).filter(
            MetaColaborador.id_eyal == ajuste.id_eyal_origem,
            MetaColaborador.mes_ref == ajuste.mes_ref
        ).first()
        
        destino = db.query(MetaColaborador).filter(
            MetaColaborador.id_eyal == ajuste.id_eyal_destino,
            MetaColaborador.mes_ref == ajuste.mes_ref
        ).first()
        
        if not origem:
            raise HTTPException(status_code=404, detail=f"Colaborador origem {ajuste.id_eyal_origem} não encontrado")
        
        if not destino:
            raise HTTPException(status_code=404, detail=f"Colaborador destino {ajuste.id_eyal_destino} não encontrado")
        
        # Criar ajuste
        novo_ajuste = AjusteMeta(
            mes_ref=mes_ref_date,
            tipo_ajuste=ajuste.tipo_ajuste,
            motivo=ajuste.motivo,
            
            id_eyal_origem=ajuste.id_eyal_origem,
            nome_origem=origem.nome,
            unidade_origem=origem.unidade,
            
            id_eyal_destino=ajuste.id_eyal_destino,
            nome_destino=destino.nome,
            unidade_destino=destino.unidade,
            
            valor_ajuste=ajuste.valor_ajuste,
            criterio=ajuste.criterio,
            observacao=ajuste.observacao,
            
            ativo=True,
            data_criacao=date.today()
        )
        
        db.add(novo_ajuste)
        db.commit()
        db.refresh(novo_ajuste)
        
        return novo_ajuste
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar ajuste: {str(e)}")


@router.get("/colaborador/{id_eyal}/calculados", response_model=AjustesCalculadosResponse)
async def get_ajustes_calculados(
    id_eyal: str,
    mes_ref: Optional[str] = Query(None, description="Mês de referência no formato YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    Retorna TODOS os ajustes calculados para um colaborador
    
    Equivalente às fórmulas SOMASES do Excel:
    - Ajustes R6 recebidos e cedidos
    - Ajustes campanhas recebidos e cedidos
    - Ajustes ADM distribuídos
    """
    try:
        if not mes_ref:
            hoje = date.today()
            mes_ref = f"{hoje.year}-{hoje.month:02d}-01"
        
        mes_ref_date = datetime.strptime(mes_ref, "%Y-%m-%d").date()
        
        # Buscar colaborador
        colaborador = db.query(MetaColaborador).filter(
            MetaColaborador.id_eyal == id_eyal,
            MetaColaborador.mes_ref == mes_ref
        ).first()
        
        if not colaborador:
            raise HTTPException(status_code=404, detail="Colaborador não encontrado")
        
        # ===== AJUSTES R6 =====
        # Recebidos (colaborador é DESTINO)
        ajustes_r6_recebidos = db.query(func.sum(AjusteMeta.valor_ajuste)).filter(
            and_(
                AjusteMeta.id_eyal_destino == id_eyal,
                AjusteMeta.mes_ref == mes_ref_date,
                AjusteMeta.tipo_ajuste == 'R6',
                AjusteMeta.ativo == True
            )
        ).scalar() or 0.0
        
        # Cedidos (colaborador é ORIGEM)
        ajustes_r6_cedidos = db.query(func.sum(AjusteMeta.valor_ajuste)).filter(
            and_(
                AjusteMeta.id_eyal_origem == id_eyal,
                AjusteMeta.mes_ref == mes_ref_date,
                AjusteMeta.tipo_ajuste == 'R6',
                AjusteMeta.ativo == True
            )
        ).scalar() or 0.0
        
        # ===== AJUSTES CAMPANHAS =====
        # Recebidos
        ajustes_campanhas_recebidos = db.query(func.sum(AjusteMeta.valor_ajuste)).filter(
            and_(
                AjusteMeta.id_eyal_destino == id_eyal,
                AjusteMeta.mes_ref == mes_ref_date,
                AjusteMeta.tipo_ajuste == 'CAMPANHA',
                AjusteMeta.ativo == True
            )
        ).scalar() or 0.0
        
        # Cedidos
        ajustes_campanhas_cedidos = db.query(func.sum(AjusteMeta.valor_ajuste)).filter(
            and_(
                AjusteMeta.id_eyal_origem == id_eyal,
                AjusteMeta.mes_ref == mes_ref_date,
                AjusteMeta.tipo_ajuste == 'CAMPANHA',
                AjusteMeta.ativo == True
            )
        ).scalar() or 0.0
        
        # ===== AJUSTES ADM (1/3 distribuído) =====
        ajustes_adm_recebidos = 0.0
        
        # Se for CENTRAL DE MARCAÇÕES, recebe 1/3 da meta ADM
        cargo_lower = (colaborador.cargo or "").lower()
        if "central" in cargo_lower and "marcações" in cargo_lower or "marcacoes" in cargo_lower:
            # Buscar total da meta ADM
            meta_adm_total = db.query(func.sum(MetaColaborador.meta_final)).filter(
                and_(
                    MetaColaborador.mes_ref == mes_ref,
                    MetaColaborador.equipe == 'ADM'
                )
            ).scalar() or 0.0
            
            ajustes_adm_recebidos = meta_adm_total / 3  # 1/3 da meta ADM
            
            print(f"--- [AJUSTES] Central de Marcações recebe 1/3 da meta ADM: R$ {ajustes_adm_recebidos:.2f} ---")
        
        # ===== TOTAL LÍQUIDO =====
        total_ajustes = (
            ajustes_r6_recebidos - ajustes_r6_cedidos +
            ajustes_campanhas_recebidos - ajustes_campanhas_cedidos +
            ajustes_adm_recebidos
        )
        
        # Buscar detalhes
        detalhes_query = db.query(AjusteMeta).filter(
            and_(
                AjusteMeta.mes_ref == mes_ref_date,
                AjusteMeta.ativo == True,
                (AjusteMeta.id_eyal_origem == id_eyal) | (AjusteMeta.id_eyal_destino == id_eyal)
            )
        ).all()
        
        detalhes = [
            {
                "tipo": ajuste.tipo_ajuste,
                "motivo": ajuste.motivo,
                "valor": ajuste.valor_ajuste,
                "direcao": "RECEBIDO" if ajuste.id_eyal_destino == id_eyal else "CEDIDO",
                "contrapart": ajuste.nome_origem if ajuste.id_eyal_destino == id_eyal else ajuste.nome_destino
            }
            for ajuste in detalhes_query
        ]
        
        return AjustesCalculadosResponse(
            id_eyal=id_eyal,
            nome=colaborador.nome,
            mes_ref=mes_ref,
            ajustes_r6_recebidos=ajustes_r6_recebidos,
            ajustes_campanhas_recebidos=ajustes_campanhas_recebidos,
            ajustes_adm_recebidos=ajustes_adm_recebidos,
            ajustes_r6_cedidos=ajustes_r6_cedidos,
            ajustes_campanhas_cedidos=ajustes_campanhas_cedidos,
            total_ajustes=total_ajustes,
            detalhes=detalhes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao calcular ajustes: {str(e)}")


@router.get("/listar", response_model=List[AjusteMetaResponse])
async def listar_ajustes(
    mes_ref: Optional[str] = Query(None, description="Mês de referência no formato YYYY-MM-DD"),
    tipo_ajuste: Optional[str] = Query(None, description="Filtrar por tipo: R6, CAMPANHA"),
    db: Session = Depends(get_db)
):
    """Lista todos os ajustes, opcionalmente filtrados por mês e tipo"""
    try:
        query = db.query(AjusteMeta).filter(AjusteMeta.ativo == True)
        
        if mes_ref:
            mes_ref_date = datetime.strptime(mes_ref, "%Y-%m-%d").date()
            query = query.filter(AjusteMeta.mes_ref == mes_ref_date)
        
        if tipo_ajuste:
            query = query.filter(AjusteMeta.tipo_ajuste == tipo_ajuste)
        
        ajustes = query.all()
        return ajustes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar ajustes: {str(e)}")


@router.delete("/{ajuste_id}")
async def desativar_ajuste(
    ajuste_id: int,
    db: Session = Depends(get_db)
):
    """Desativa (soft delete) um ajuste"""
    try:
        ajuste = db.query(AjusteMeta).filter(AjusteMeta.id == ajuste_id).first()
        
        if not ajuste:
            raise HTTPException(status_code=404, detail="Ajuste não encontrado")
        
        ajuste.ativo = False
        db.commit()
        
        return {"message": "Ajuste desativado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao desativar ajuste: {str(e)}")
