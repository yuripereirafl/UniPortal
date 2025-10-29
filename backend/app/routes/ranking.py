from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from typing import List, Dict, Any
from datetime import datetime
import logging

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/top-vendedores")
async def get_top_vendedores(
    mes_ref: str = "2025-09-01",
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    Retorna o ranking dos top 5 vendedores baseado nos dados reais de vendas
    """
    try:
        # Query para buscar os top vendedores por valor total (agregando todos os tipos de procedimento)
        query = """
            SELECT 
                quem_agendou as nome,
                TRIM(unidade) as unidade,
                STRING_AGG(DISTINCT tipo_grupo, ', ') as tipos_procedimentos,
                SUM(total_realizado) as total_valor,
                SUM(total_registros) as total_vendas,
                COUNT(*) as total_procedimentos
            FROM rh_homologacao.realizado_colaborador 
            WHERE mes_ref = :mes_ref
            AND quem_agendou IS NOT NULL 
            AND quem_agendou NOT IN ('WHATS_WEB', 'SITE_WEB')
            AND total_realizado > 0
            GROUP BY quem_agendou, TRIM(unidade)
            ORDER BY total_vendas DESC
            LIMIT :limit
        """
        
        result = db.execute(text(query), {"mes_ref": mes_ref, "limit": limit}).fetchall()
        
        # Formatar os resultados
        vendedores = []
        for i, row in enumerate(result):
            # Calcular percentual da meta (usando uma meta base de R$ 15.000)
            meta_base = 15000
            percentual_meta = round((row.total_valor / meta_base) * 100, 1) if row.total_valor else 0
            
            # Determinar cargo baseado na performance
            if percentual_meta >= 125:
                cargo = "Vendedor Sênior"
            elif percentual_meta >= 110:
                cargo = "Consultor de Vendas"
            elif percentual_meta >= 100:
                cargo = "Supervisora de Vendas"
            elif percentual_meta >= 90:
                cargo = "Vendedor Pleno"
            else:
                cargo = "Consultora Especializada"
            
            # Determinar badge baseado na posição
            badges = {0: "Campeã", 1: "Vice", 2: "Bronze", 3: "", 4: ""}
            
            vendedor = {
                "posicao": i + 1,
                "nome": row.nome,
                "cargo": cargo,
                "unidade": row.unidade,
                "tipos_procedimentos": row.tipos_procedimentos,
                "total_valor": float(row.total_valor),
                "total_vendas": int(row.total_vendas),
                "total_procedimentos": int(row.total_procedimentos),
                "percentual_meta": percentual_meta,
                "badge": badges.get(i, ""),
                "iniciais": get_iniciais(row.nome)
            }
            vendedores.append(vendedor)
            
        return {
            "success": True,
            "data": vendedores,
            "mes_referencia": format_mes_referencia(mes_ref)
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar ranking: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ranking: {str(e)}")

@router.get("/estatisticas-gerais")
async def get_estatisticas_gerais(
    mes_ref: str = "2025-09-01",
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas gerais para o card de motivação
    """
    try:
        query = """
            SELECT 
                SUM(total_registros) as vendas_totais,
                SUM(total_realizado) as faturamento_total,
                COUNT(DISTINCT quem_agendou) as vendedores_ativos
            FROM rh_homologacao.realizado_colaborador 
            WHERE mes_ref = :mes_ref
            AND quem_agendou IS NOT NULL 
            AND quem_agendou NOT IN ('WHATS_WEB', 'SITE_WEB')
            AND total_realizado > 0
        """
        
        result = db.execute(text(query), {"mes_ref": mes_ref}).fetchone()
        
        if result:
            # Calcular meta da equipe (assumindo meta total de R$ 500.000)
            meta_equipe_total = 500000
            percentual_meta_equipe = round((result.faturamento_total / meta_equipe_total) * 100, 1)
            
            return {
                "success": True,
                "data": {
                    "vendas_totais": int(result.vendas_totais or 0),
                    "faturamento_total": float(result.faturamento_total or 0),
                    "percentual_meta_equipe": percentual_meta_equipe,
                    "vendedores_ativos": int(result.vendedores_ativos or 0)
                },
                "mes_referencia": format_mes_referencia(mes_ref)
            }
        else:
            return {
                "success": True,
                "data": {
                    "vendas_totais": 0,
                    "faturamento_total": 0,
                    "percentual_meta_equipe": 0,
                    "vendedores_ativos": 0
                },
                "mes_referencia": format_mes_referencia(mes_ref)
            }
            
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatísticas: {str(e)}")

def get_iniciais(nome: str) -> str:
    """Extrai as iniciais do nome"""
    if not nome:
        return "??"
    palavras = nome.split()
    if len(palavras) >= 2:
        return (palavras[0][0] + palavras[-1][0]).upper()
    else:
        return nome[:2].upper()

def format_mes_referencia(mes_ref: str) -> str:
    """Formata a data de referência para exibição"""
    try:
        date_obj = datetime.strptime(mes_ref, "%Y-%m-%d")
        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        return f"{meses[date_obj.month]} {date_obj.year}"
    except:
        return "Setembro 2025"