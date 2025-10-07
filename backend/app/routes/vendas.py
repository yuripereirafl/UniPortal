from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

from app.dependencies import get_db
from app.models.vendas import BaseCampanhas
from app.schemas.vendas import VendasResponse, ResumoVendas, DetalheVenda, VendasPorGrupo

router = APIRouter(
    prefix="/vendas",
    tags=["Vendas"]
)


def classificar_grupo(grupo_exames: str, abrev_exame: str) -> str:
    """Classifica a venda em uma categoria específica"""
    if not grupo_exames:
        grupo_exames = ""
    if not abrev_exame:
        abrev_exame = ""
    
    grupo_upper = grupo_exames.strip().upper()
    abrev_upper = abrev_exame.strip().upper()
    
    if grupo_upper == 'ODONTO':
        return 'ODONTO'
    elif grupo_upper == 'CHECK UP':
        return 'CHECK UP'
    elif grupo_upper == 'BABYCLICK':
        return 'BabyClick'
    elif 'DR CENTRAL' in abrev_upper:
        return 'DR CENTRAL'
    else:
        return 'ORÇAMENTOS'


@router.get("/colaborador/{cod_usuario}", response_model=VendasResponse)
async def get_vendas_colaborador(
    cod_usuario: str,
    mes_ref: Optional[str] = Query(None, description="Mês de referência no formato YYYY-MM"),
    db: Session = Depends(get_db)
):
    """Retorna todas as vendas de um colaborador específico"""
    try:
        if mes_ref:
            try:
                mes_referencia = datetime.strptime(mes_ref, "%Y-%m").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM")
        else:
            hoje = date.today()
            mes_referencia = date(hoje.year, hoje.month, 1)
        
        vendas = db.query(BaseCampanhas).filter(
            and_(
                BaseCampanhas.cod_usuario == cod_usuario,
                extract('year', BaseCampanhas.mes) == mes_referencia.year,
                extract('month', BaseCampanhas.mes) == mes_referencia.month
            )
        ).all()
        
        if not vendas:
            return VendasResponse(
                success=True,
                resumo=None,
                detalhes=[],
                message=f"Nenhuma venda encontrada para o colaborador {cod_usuario}"
            )
        
        contadores = {
            'odonto': 0,
            'check_up': 0,
            'baby_click': 0,
            'dr_central': 0,
            'orcamentos': 0
        }
        
        vendas_por_grupo_dict = {}
        detalhes_list = []
        valor_total = 0.0
        
        for venda in vendas:
            categoria = classificar_grupo(venda.grupo_exames or "", venda.abrev_exame or "")
            
            if categoria == 'ODONTO':
                contadores['odonto'] += 1
            elif categoria == 'CHECK UP':
                contadores['check_up'] += 1
            elif categoria == 'BabyClick':
                contadores['baby_click'] += 1
            elif categoria == 'DR CENTRAL':
                contadores['dr_central'] += 1
            else:
                contadores['orcamentos'] += 1
            
            if categoria not in vendas_por_grupo_dict:
                vendas_por_grupo_dict[categoria] = {
                    'quantidade': 0,
                    'valor_total': 0.0
                }
            
            valor = float(venda.valor_original_proc) if venda.valor_original_proc else 0.0
            vendas_por_grupo_dict[categoria]['quantidade'] += 1
            vendas_por_grupo_dict[categoria]['valor_total'] += valor
            valor_total += valor
            
            detalhes_list.append(DetalheVenda(
                mes=venda.mes,
                data_agenda=venda.data_agenda,
                cod_paciente=venda.cod_paciente,
                nome_exame=venda.nome_exame_ajustado or "",
                grupo_exames=venda.grupo_exames or "",
                valor=valor,
                unidade=venda.unidade or "",
                abrev_exame=venda.abrev_exame or ""
            ))
        
        vendas_por_grupo_list = [
            VendasPorGrupo(
                grupo=grupo,
                quantidade=dados['quantidade'],
                valor_total=dados['valor_total']
            )
            for grupo, dados in vendas_por_grupo_dict.items()
        ]
        
        nome_usuario = vendas[0].usuario_agendo if vendas else cod_usuario
        resumo = ResumoVendas(
            cod_usuario=cod_usuario,
            nome_usuario=nome_usuario,
            mes_referencia=mes_referencia,
            total_vendas=len(vendas),
            valor_total=valor_total,
            odonto=contadores['odonto'],
            check_up=contadores['check_up'],
            baby_click=contadores['baby_click'],
            dr_central=contadores['dr_central'],
            orcamentos=contadores['orcamentos'],
            vendas_por_grupo=vendas_por_grupo_list
        )
        
        return VendasResponse(
            success=True,
            resumo=resumo,
            detalhes=detalhes_list,
            message=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar vendas: {str(e)}")


@router.get("/grupo/{grupo}", response_model=VendasResponse)
async def get_vendas_por_grupo(
    grupo: str,
    mes_ref: Optional[str] = Query(None, description="Mês de referência no formato YYYY-MM"),
    db: Session = Depends(get_db)
):
    """Retorna todas as vendas de um grupo específico"""
    try:
        if mes_ref:
            try:
                mes_referencia = datetime.strptime(mes_ref, "%Y-%m").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM")
        else:
            hoje = date.today()
            mes_referencia = date(hoje.year, hoje.month, 1)
        
        vendas_mes = db.query(BaseCampanhas).filter(
            and_(
                extract('year', BaseCampanhas.mes) == mes_referencia.year,
                extract('month', BaseCampanhas.mes) == mes_referencia.month
            )
        ).all()
        
        vendas_filtradas = []
        for venda in vendas_mes:
            categoria = classificar_grupo(venda.grupo_exames or "", venda.abrev_exame or "")
            if categoria.upper() == grupo.upper():
                vendas_filtradas.append(venda)
        
        if not vendas_filtradas:
            return VendasResponse(
                success=True,
                resumo=None,
                detalhes=[],
                message=f"Nenhuma venda encontrada para o grupo {grupo}"
            )
        
        detalhes_list = []
        valor_total = 0.0
        
        for venda in vendas_filtradas:
            valor = float(venda.valor_original_proc) if venda.valor_original_proc else 0.0
            valor_total += valor
            
            detalhes_list.append(DetalheVenda(
                mes=venda.mes,
                data_agenda=venda.data_agenda,
                cod_paciente=venda.cod_paciente,
                nome_exame=venda.nome_exame_ajustado or "",
                grupo_exames=venda.grupo_exames or "",
                valor=valor,
                unidade=venda.unidade or "",
                abrev_exame=venda.abrev_exame or ""
            ))
        
        resumo = ResumoVendas(
            cod_usuario="TODOS",
            nome_usuario=f"Grupo {grupo}",
            mes_referencia=mes_referencia,
            total_vendas=len(vendas_filtradas),
            valor_total=valor_total,
            vendas_por_grupo=[
                VendasPorGrupo(
                    grupo=grupo,
                    quantidade=len(vendas_filtradas),
                    valor_total=valor_total
                )
            ]
        )
        
        return VendasResponse(
            success=True,
            resumo=resumo,
            detalhes=detalhes_list,
            message=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar vendas do grupo: {str(e)}")
