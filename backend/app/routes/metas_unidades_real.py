from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List, Optional
from datetime import datetime, date

from app.database import get_db

router = APIRouter()

@router.get("/dashboard")
def dashboard_unidades_real(
    mes_ref: Optional[str] = Query(None, description="Mês de referência (YYYY-MM)"),
    db: Session = Depends(get_db)
):
    """
    Dashboard de metas das unidades usando dados reais do banco.
    Agrega dados de metas_unidade e realizado_colaborador.
    """
    print("--- [DASHBOARD UNIDADES REAL] Iniciando ---")
    
    # Se não foi fornecido mes_ref, usar o mês atual
    if not mes_ref:
        mes_ref = datetime.now().strftime("%Y-%m")
    
    # Converter para formato de data
    try:
        ano, mes = mes_ref.split('-')
        data_ref = f"{ano}-{mes}-01"
    except:
        data_ref = datetime.now().strftime("%Y-%m-01")
    
    print(f"--- [DASHBOARD UNIDADES REAL] Data de referência: {data_ref} ---")
    
    try:
        # 1. Buscar metas das unidades
        query_metas = text("""
            SELECT 
                TRIM(unidade) as unidade,
                valor_meta as meta
            FROM rh_homologacao.metas_unidade 
            WHERE mes_ref = :data_ref
            ORDER BY unidade
        """)
        
        result_metas = db.execute(query_metas, {"data_ref": data_ref}).fetchall()
        print(f"--- [DASHBOARD UNIDADES REAL] Encontradas {len(result_metas)} metas ---")
        
        # 2. Buscar realizados agregados por unidade
        query_realizados = text("""
            SELECT 
                TRIM(unidade) as unidade,
                SUM(total_realizado) as realizado
            FROM rh_homologacao.realizado_colaborador 
            WHERE mes_ref = :data_ref
            AND unidade IS NOT NULL
            GROUP BY TRIM(unidade)
            ORDER BY unidade
        """)
        
        result_realizados = db.execute(query_realizados, {"data_ref": data_ref}).fetchall()
        print(f"--- [DASHBOARD UNIDADES REAL] Encontrados realizados de {len(result_realizados)} unidades ---")
        
        # 3. Combinar dados de metas e realizados
        dados_unidades = []
        total_meta = 0
        total_realizado = 0
        
        # Criar dict de realizados para lookup rápido
        realizados_dict = {row.unidade: float(row.realizado or 0) for row in result_realizados}
        
        for i, meta_row in enumerate(result_metas):
            unidade = meta_row.unidade
            meta = float(meta_row.meta or 0)
            realizado = realizados_dict.get(unidade, 0)
            
            # Calcular indicadores
            diferenca = realizado - meta
            percentual = (realizado / meta * 100) if meta > 0 else 0
            
            unidade_data = {
                "id": i + 1,
                "unidade": unidade,
                "mes": mes_ref,
                "meta": meta,
                "realizado": realizado,
                "diferenca": diferenca,
                "percentual_atingimento": percentual,
                "meta_formatada": f"R$ {meta:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                "realizado_formatado": f"R$ {realizado:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                "diferenca_formatada": f"R$ {diferenca:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            }
            
            dados_unidades.append(unidade_data)
            total_meta += meta
            total_realizado += realizado
        
        # 4. Buscar total de colaboradores únicos
        query_colaboradores = text("""
            SELECT 
                COUNT(DISTINCT id_eyal) as total_colaboradores,
                SUM(CASE WHEN tipo_grupo = 'ODONTO' THEN total_realizado ELSE 0 END) as total_odonto,
                SUM(CASE WHEN tipo_grupo = 'EXAMES' THEN total_realizado ELSE 0 END) as total_exames,
                SUM(CASE WHEN tipo_grupo = 'CONSULTAS' THEN total_realizado ELSE 0 END) as total_consultas
            FROM rh_homologacao.realizado_colaborador 
            WHERE mes_ref = :data_ref
            AND unidade IS NOT NULL
        """)
        
        result_colaboradores = db.execute(query_colaboradores, {"data_ref": data_ref}).fetchone()
        total_colaboradores = result_colaboradores.total_colaboradores if result_colaboradores else 0
        
        # 5. Calcular resumo geral
        percentual_medio = (total_realizado / total_meta * 100) if total_meta > 0 else 0
        
        resumo = {
            "total_unidades": len(dados_unidades),
            "total_colaboradores": total_colaboradores,
            "meta_total": total_meta,
            "realizado_total": total_realizado,
            "percentual_medio": percentual_medio,
            "meta_total_formatada": f"R$ {total_meta:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "realizado_total_formatado": f"R$ {total_realizado:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "totais_por_categoria": {
                "odonto": {
                    "valor": float(result_colaboradores.total_odonto or 0),
                    "valor_formatado": f"R$ {float(result_colaboradores.total_odonto or 0):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                },
                "exames": {
                    "valor": float(result_colaboradores.total_exames or 0),
                    "valor_formatado": f"R$ {float(result_colaboradores.total_exames or 0):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                },
                "consultas": {
                    "valor": float(result_colaboradores.total_consultas or 0),
                    "valor_formatado": f"R$ {float(result_colaboradores.total_consultas or 0):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                }
            }
        }
        
        print(f"--- [DASHBOARD UNIDADES REAL] Resumo: {len(dados_unidades)} unidades, {total_colaboradores} colaboradores, Meta: {total_meta:.2f}, Realizado: {total_realizado:.2f} ---")
        
        return {
            "unidades": dados_unidades,
            "resumo": resumo
        }
        
    except Exception as e:
        print(f"--- [DASHBOARD UNIDADES REAL] Erro: {e} ---")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados: {str(e)}")

@router.get("/unidades")
def listar_unidades_reais(db: Session = Depends(get_db)):
    """
    Lista todas as unidades disponíveis no banco.
    """
    try:
        query = text("""
            SELECT DISTINCT TRIM(unidade) as unidade
            FROM rh_homologacao.metas_unidade 
            WHERE unidade IS NOT NULL
            ORDER BY unidade
        """)
        
        result = db.execute(query).fetchall()
        unidades = [row.unidade for row in result]
        
        return {"unidades": unidades}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar unidades: {str(e)}")

@router.get("/meses")
def listar_meses_disponiveis(db: Session = Depends(get_db)):
    """
    Lista todos os meses disponíveis no banco.
    """
    try:
        query = text("""
            SELECT DISTINCT 
                TO_CHAR(mes_ref, 'YYYY-MM') as mes
            FROM rh_homologacao.metas_unidade 
            ORDER BY mes DESC
        """)
        
        result = db.execute(query).fetchall()
        meses = [row.mes for row in result]
        
        return {"meses": meses}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar meses: {str(e)}")

@router.get("/rankings")
def obter_rankings_por_categoria(
    mes_ref: Optional[str] = Query(None, description="Mês de referência (YYYY-MM)"),
    unidade: Optional[str] = Query(None, description="Filtrar por unidade"),
    db: Session = Depends(get_db)
):
    """
    Obtém rankings dos top performers por categoria.
    """
    if not mes_ref:
        mes_ref = datetime.now().strftime("%Y-%m")
    
    try:
        # Converter para formato de data
        ano, mes = mes_ref.split('-')
        data_ref = f"{ano}-{mes}-01"
        
        rankings = {}
        
        # Filtro de unidade
        filtro_unidade = ""
        params = {"data_ref": data_ref}
        if unidade and unidade.strip():
            filtro_unidade = "AND TRIM(unidade) = :unidade"
            params["unidade"] = unidade.strip()
        
        # Ranking ODONTO
        query_odonto = text(f"""
            SELECT 
                quem_agendou,
                TRIM(unidade) as unidade,
                SUM(total_realizado) as total_realizado,
                SUM(total_registros) as total_registros
            FROM rh_homologacao.realizado_colaborador 
            WHERE mes_ref = :data_ref 
            AND tipo_grupo = 'ODONTO'
            AND quem_agendou IS NOT NULL
            AND quem_agendou NOT IN ('WHATS_WEB', 'SITE_WEB')
            {filtro_unidade}
            GROUP BY quem_agendou, TRIM(unidade)
            ORDER BY total_realizado DESC
            LIMIT 10
        """)
        
        result_odonto = db.execute(query_odonto, params).fetchall()
        rankings["odonto"] = [
            {
                "posicao": i + 1,
                "nome": row.quem_agendou,
                "unidade": row.unidade,
                "valor": float(row.total_realizado),
                "registros": row.total_registros,
                "valor_formatado": f"R$ {float(row.total_realizado):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            }
            for i, row in enumerate(result_odonto)
        ]
        
        # Ranking EXAMES
        query_exames = text(f"""
            SELECT 
                quem_agendou,
                TRIM(unidade) as unidade,
                SUM(total_realizado) as total_realizado,
                SUM(total_registros) as total_registros
            FROM rh_homologacao.realizado_colaborador 
            WHERE mes_ref = :data_ref 
            AND tipo_grupo = 'EXAMES'
            AND quem_agendou IS NOT NULL
            AND quem_agendou NOT IN ('WHATS_WEB', 'SITE_WEB')
            {filtro_unidade}
            GROUP BY quem_agendou, TRIM(unidade)
            ORDER BY total_realizado DESC
            LIMIT 10
        """)
        
        result_exames = db.execute(query_exames, params).fetchall()
        rankings["exames"] = [
            {
                "posicao": i + 1,
                "nome": row.quem_agendou,
                "unidade": row.unidade,
                "valor": float(row.total_realizado),
                "registros": row.total_registros,
                "valor_formatado": f"R$ {float(row.total_realizado):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            }
            for i, row in enumerate(result_exames)
        ]
        
        # Ranking CONSULTAS
        query_consultas = text(f"""
            SELECT 
                quem_agendou,
                TRIM(unidade) as unidade,
                SUM(total_realizado) as total_realizado,
                SUM(total_registros) as total_registros
            FROM rh_homologacao.realizado_colaborador 
            WHERE mes_ref = :data_ref 
            AND tipo_grupo = 'CONSULTAS'
            AND quem_agendou IS NOT NULL
            AND quem_agendou NOT IN ('WHATS_WEB', 'SITE_WEB')
            {filtro_unidade}
            GROUP BY quem_agendou, TRIM(unidade)
            ORDER BY total_realizado DESC
            LIMIT 10
        """)
        
        result_consultas = db.execute(query_consultas, params).fetchall()
        rankings["consultas"] = [
            {
                "posicao": i + 1,
                "nome": row.quem_agendou,
                "unidade": row.unidade,
                "valor": float(row.total_realizado),
                "registros": row.total_registros,
                "valor_formatado": f"R$ {float(row.total_realizado):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            }
            for i, row in enumerate(result_consultas)
        ]
        
        # Ranking CHECKUPS (usando uma subconsulta de EXAMES filtrada)
        query_checkups = text(f"""
            SELECT 
                quem_agendou,
                TRIM(unidade) as unidade,
                SUM(total_realizado) as total_realizado,
                SUM(total_registros) as total_registros
            FROM rh_homologacao.realizado_colaborador 
            WHERE mes_ref = :data_ref 
            AND tipo_grupo = 'EXAMES'
            AND quem_agendou IS NOT NULL
            AND quem_agendou NOT IN ('WHATS_WEB', 'SITE_WEB')
            {filtro_unidade}
            GROUP BY quem_agendou, TRIM(unidade)
            ORDER BY total_registros DESC
            LIMIT 10
        """)
        
        result_checkups = db.execute(query_checkups, params).fetchall()
        rankings["checkups"] = [
            {
                "posicao": i + 1,
                "nome": row.quem_agendou,
                "unidade": row.unidade,
                "valor": float(row.total_realizado),
                "registros": row.total_registros,
                "valor_formatado": f"R$ {float(row.total_realizado):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            }
            for i, row in enumerate(result_checkups)
        ]
        
        return {
            "rankings": rankings,
            "mes_ref": mes_ref,
            "unidade_filtro": unidade
        }
        
    except Exception as e:
        print(f"--- [RANKINGS] Erro: {e} ---")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar rankings: {str(e)}")


@router.get("/rankings-top10")
async def get_rankings_top10(
    mes_ref: Optional[str] = Query(None, description="Mês de referência (YYYY-MM)"), 
    unidade: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Endpoint para retornar top 10 vendedores reais por categoria
    """
    # Se não fornecido, usar mês atual
    if not mes_ref:
        mes_ref = datetime.now().strftime("%Y-%m")
    
    print(f"--- [RANKINGS TOP 10] Iniciando para {mes_ref}, unidade: {unidade} ---")
    
    try:
        # Converter para formato de data
        try:
            ano, mes = mes_ref.split('-')
            data_ref = f"{ano}-{mes}-01"
        except:
            # Fallback para mês atual se houver erro no parse
            data_ref = datetime.now().strftime("%Y-%m-01")
        
        # Query para buscar top 10 vendedores por categoria
        filtro_unidade = ""
        params = {"data_ref": data_ref}
        
        if unidade:
            filtro_unidade = " AND TRIM(unidade) = :unidade"
            params["unidade"] = unidade
        
        # Buscar todas as categorias disponíveis
        query_categorias = text(f"""
            SELECT DISTINCT tipo_grupo
            FROM rh_homologacao.realizado_colaborador 
            WHERE mes_ref = :data_ref
            AND quem_agendou IS NOT NULL 
            AND quem_agendou NOT IN ('WHATS_WEB', 'SITE_WEB')
            {filtro_unidade}
            ORDER BY tipo_grupo
        """)
        
        categorias = db.execute(query_categorias, params).fetchall()
        print(f"--- [RANKINGS TOP 10] Categorias encontradas: {[c.tipo_grupo for c in categorias]} ---")
        
        rankings_por_categoria = []
        
        # Para cada categoria, buscar top 10
        for categoria_row in categorias:
            categoria = categoria_row.tipo_grupo
            
            query_ranking = text(f"""
                SELECT 
                    quem_agendou as nome_vendedor,
                    TRIM(unidade) as unidade,
                    SUM(total_realizado) as total_valor,
                    SUM(total_registros) as quantidade_procedimentos
                FROM rh_homologacao.realizado_colaborador 
                WHERE mes_ref = :data_ref
                AND tipo_grupo = :categoria
                AND quem_agendou IS NOT NULL 
                AND quem_agendou NOT IN ('WHATS_WEB', 'SITE_WEB')
                {filtro_unidade}
                GROUP BY quem_agendou, TRIM(unidade)
                ORDER BY total_valor DESC
                LIMIT 10
            """)
            
            params_categoria = params.copy()
            params_categoria["categoria"] = categoria
            
            vendedores = db.execute(query_ranking, params_categoria).fetchall()
            
            # Definir ícones para cada categoria
            icones_categoria = {
                "EXAMES": "fas fa-vial",
                "CONSULTAS": "fas fa-stethoscope", 
                "ODONTO": "fas fa-tooth",
                "CHECKUPS": "fas fa-heartbeat"
            }
            
            # Formatar vendedores
            vendedores_formatados = []
            for i, vendedor in enumerate(vendedores):
                vendedores_formatados.append({
                    "posicao": i + 1,
                    "nome": vendedor.nome_vendedor,
                    "unidade": vendedor.unidade,
                    "valor": float(vendedor.total_valor or 0),
                    "quantidade": int(vendedor.quantidade_procedimentos or 0),
                    "valor_formatado": f"R$ {float(vendedor.total_valor or 0):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
                })
            
            rankings_por_categoria.append({
                "categoria": categoria,
                "icone": icones_categoria.get(categoria, "fas fa-chart-bar"),
                "vendedores": vendedores_formatados,
                "total_vendedores": len(vendedores_formatados)
            })
            
            print(f"--- [RANKINGS TOP 10] {categoria}: {len(vendedores)} vendedores ---")
        
        return {
            "rankings": rankings_por_categoria,
            "periodo": mes_ref,
            "unidade_filtro": unidade,
            "total_categorias": len(rankings_por_categoria)
        }
        
    except Exception as e:
        print(f"--- [RANKINGS TOP 10] Erro: {e} ---")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar rankings: {str(e)}")