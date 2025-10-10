from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from app.database import get_db
from app.models.orcamento import Orcamento
from app.schemas.orcamento import OrcamentoResponse
from typing import Optional
from datetime import datetime

router = APIRouter(
    prefix="/orcamentos",
    tags=["Orçamentos"]
)


@router.get("/colaborador/{cod_usuario}")
def get_orcamentos_colaborador(
    cod_usuario: int,
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    📋 Orçamentos do Colaborador
    
    Retorna a quantidade e detalhes dos orçamentos realizados pelo colaborador.
    
    Args:
        cod_usuario: Código do usuário (ID Eyal)
        mes_ref: Mês de referência (formato YYYY-MM, opcional - usa mês atual se omitido)
    
    Returns:
        Dados de orçamentos do colaborador (total, confirmados, pendentes, etc.)
    """
    try:
        # Determinar mês de referência
        if mes_ref:
            # Converter YYYY-MM para ano e mês
            ano = int(mes_ref.split('-')[0])
            mes = int(mes_ref.split('-')[1])
        else:
            # Usar mês atual
            hoje = datetime.now()
            ano = hoje.year
            mes = hoje.month
        
        # Query base - orçamentos do colaborador no mês
        query = db.query(Orcamento).filter(
            Orcamento.cod_usuario == cod_usuario,
            extract('year', Orcamento.criado) == ano,
            extract('month', Orcamento.criado) == mes
        )
        
        # Executar query
        orcamentos = query.all()
        
        if not orcamentos:
            return {
                "success": False,
                "colaborador": {
                    "cod_usuario": cod_usuario,
                    "nome": None
                },
                "orcamentos": {
                    "total": 0,
                    "confirmados": 0,
                    "pendentes": 0,
                    "taxa_confirmacao": 0.0,
                    "mes_referencia": f"{ano}-{mes:02d}"
                },
                "message": f"Nenhum orçamento encontrado para o colaborador {cod_usuario} no mês {mes_ref or f'{ano}-{mes:02d}'}"
            }
        
        # Processar dados
        total_orcamentos = len(orcamentos)
        confirmados = sum(1 for o in orcamentos if o.confirmado == 'S')
        pendentes = sum(1 for o in orcamentos if o.confirmado != 'S')
        taxa_confirmacao = (confirmados / total_orcamentos * 100) if total_orcamentos > 0 else 0
        
        # Pegar nome do colaborador do primeiro registro
        nome_colaborador = orcamentos[0].colab_orcou if orcamentos[0].colab_orcou else None
        
        # Agrupar por unidade
        orcamentos_por_unidade = {}
        for orc in orcamentos:
            unidade = orc.unidade_usuario or 'SEM UNIDADE'
            if unidade not in orcamentos_por_unidade:
                orcamentos_por_unidade[unidade] = {
                    'total': 0,
                    'confirmados': 0,
                    'pendentes': 0
                }
            orcamentos_por_unidade[unidade]['total'] += 1
            if orc.confirmado == 'S':
                orcamentos_por_unidade[unidade]['confirmados'] += 1
            else:
                orcamentos_por_unidade[unidade]['pendentes'] += 1
        
        return {
            "success": True,
            "colaborador": {
                "cod_usuario": cod_usuario,
                "nome": nome_colaborador
            },
            "orcamentos": {
                "total": total_orcamentos,
                "confirmados": confirmados,
                "pendentes": pendentes,
                "taxa_confirmacao": round(taxa_confirmacao, 2),
                "mes_referencia": f"{ano}-{mes:02d}",
                "por_unidade": orcamentos_por_unidade
            },
            "message": None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar orçamentos: {str(e)}"
        )


@router.get("/historico/{cod_usuario}")
def get_historico_orcamentos(
    cod_usuario: int,
    limite: int = 12,
    db: Session = Depends(get_db)
):
    """
    📊 Histórico de Orçamentos
    
    Retorna o histórico mensal de orçamentos do colaborador.
    
    Args:
        cod_usuario: Código do usuário
        limite: Quantidade de meses (padrão: 12)
    
    Returns:
        Histórico mensal de orçamentos
    """
    try:
        # Query para obter dados agrupados por mês
        resultados = db.query(
            extract('year', Orcamento.criado).label('ano'),
            extract('month', Orcamento.criado).label('mes'),
            func.count(Orcamento.seq_orcamento).label('total'),
            func.sum(
                func.case((Orcamento.confirmado == 'S', 1), else_=0)
            ).label('confirmados')
        ).filter(
            Orcamento.cod_usuario == cod_usuario
        ).group_by(
            extract('year', Orcamento.criado),
            extract('month', Orcamento.criado)
        ).order_by(
            extract('year', Orcamento.criado).desc(),
            extract('month', Orcamento.criado).desc()
        ).limit(limite).all()
        
        if not resultados:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum histórico encontrado para o colaborador {cod_usuario}"
            )
        
        # Pegar nome do colaborador
        primeiro_orcamento = db.query(Orcamento).filter(
            Orcamento.cod_usuario == cod_usuario
        ).first()
        
        nome_colaborador = primeiro_orcamento.colab_orcou if primeiro_orcamento and primeiro_orcamento.colab_orcou else None
        
        # Formatar resposta
        historico = []
        for r in resultados:
            ano = int(r.ano)
            mes = int(r.mes)
            total = int(r.total)
            confirmados = int(r.confirmados or 0)
            pendentes = total - confirmados
            taxa = (confirmados / total * 100) if total > 0 else 0
            
            historico.append({
                "mes_referencia": f"{ano}-{mes:02d}",
                "total": total,
                "confirmados": confirmados,
                "pendentes": pendentes,
                "taxa_confirmacao": round(taxa, 2)
            })
        
        return {
            "success": True,
            "colaborador": {
                "cod_usuario": cod_usuario,
                "nome": nome_colaborador
            },
            "historico": historico,
            "total_meses": len(historico)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar histórico: {str(e)}"
        )


@router.get("/equipe/{nome_equipe}")
def get_orcamentos_equipe(
    nome_equipe: str,
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    👥 Orçamentos da Equipe/Unidade
    
    Retorna resumo de orçamentos de toda uma equipe/unidade.
    
    Args:
        nome_equipe: Nome da equipe/unidade
        mes_ref: Mês de referência (opcional)
    
    Returns:
        Resumo de orçamentos da equipe
    """
    try:
        # Determinar mês de referência
        if mes_ref:
            ano = int(mes_ref.split('-')[0])
            mes = int(mes_ref.split('-')[1])
        else:
            hoje = datetime.now()
            ano = hoje.year
            mes = hoje.month
        
        # Query base
        query = db.query(Orcamento).filter(
            Orcamento.unidade_usuario.ilike(f"%{nome_equipe}%"),
            extract('year', Orcamento.criado) == ano,
            extract('month', Orcamento.criado) == mes
        )
        
        orcamentos = query.all()
        
        if not orcamentos:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum orçamento encontrado para a equipe {nome_equipe}"
            )
        
        # Processar dados
        total_orcamentos = len(orcamentos)
        confirmados = sum(1 for o in orcamentos if o.confirmado == 'S')
        pendentes = total_orcamentos - confirmados
        taxa_confirmacao = (confirmados / total_orcamentos * 100) if total_orcamentos > 0 else 0
        
        # Agrupar por colaborador
        por_colaborador = {}
        for orc in orcamentos:
            cod = orc.cod_usuario
            if cod not in por_colaborador:
                por_colaborador[cod] = {
                    'cod_usuario': cod,
                    'nome': orc.colab_orcou,
                    'total': 0,
                    'confirmados': 0
                }
            por_colaborador[cod]['total'] += 1
            if orc.confirmado == 'S':
                por_colaborador[cod]['confirmados'] += 1
        
        # Ordenar por total
        colaboradores = sorted(
            por_colaborador.values(),
            key=lambda x: x['total'],
            reverse=True
        )
        
        return {
            "success": True,
            "equipe": nome_equipe,
            "mes_referencia": f"{ano}-{mes:02d}",
            "resumo": {
                "total_orcamentos": total_orcamentos,
                "confirmados": confirmados,
                "pendentes": pendentes,
                "taxa_confirmacao": round(taxa_confirmacao, 2),
                "total_colaboradores": len(colaboradores)
            },
            "colaboradores": colaboradores
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar orçamentos da equipe: {str(e)}"
        )
