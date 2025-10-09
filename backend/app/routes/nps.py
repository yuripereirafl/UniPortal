from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models.resultado_csat import ResultadoCSAT
from app.schemas.resultado_csat import ResultadoCSATResponse
from sqlalchemy import func, desc

router = APIRouter(
    prefix="/nps",
    tags=["NPS/CSAT"]
)


@router.get("/colaborador/{cod_usuario}")
def get_nps_colaborador(
    cod_usuario: int,
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    🌟 Retorna o NPS/CSAT de um colaborador
    
    Busca na tabela resultadocsat o NPS do colaborador baseado no cod_usuario.
    
    Args:
        cod_usuario: Código do usuário (ID Eyal)
        mes_ref: Mês de referência (formato YYYY-MM). Se não fornecido, usa o mais recente.
        
    Returns:
        Dados de NPS/CSAT do colaborador incluindo:
        - NPS (Net Promoter Score)
        - Quantidade de detratores, neutros e promotores
        - Distribuição das notas (1 a 5)
        - Quantidade total de avaliações
    """
    try:
        # Construir query base
        query = db.query(ResultadoCSAT).filter(
            ResultadoCSAT.cod_usuario == cod_usuario
        )
        
        # Se mes_ref foi fornecido, filtrar pelo mês
        if mes_ref:
            # Converter YYYY-MM para timestamp do primeiro dia do mês
            try:
                data_ref = datetime.strptime(f"{mes_ref}-01", "%Y-%m-%d")
                # Filtrar pelo mês e ano
                query = query.filter(
                    func.extract('year', ResultadoCSAT.mes) == data_ref.year,
                    func.extract('month', ResultadoCSAT.mes) == data_ref.month
                )
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Formato de mês inválido: {mes_ref}. Use YYYY-MM"
                )
        
        # Ordenar por mês mais recente e pegar o primeiro
        resultado = query.order_by(desc(ResultadoCSAT.mes)).first()
        
        if not resultado:
            return {
                "success": False,
                "colaborador": {
                    "cod_usuario": cod_usuario,
                    "nome": None
                },
                "nps_data": {
                    "nps": None,
                    "qtd_detrator": 0,
                    "qtd_neutro": 0,
                    "qtd_promotor": 0,
                    "qtd_total": 0,
                    "mes_referencia": mes_ref
                },
                "message": f"Nenhum dado de NPS encontrado para o colaborador {cod_usuario}" + 
                          (f" no mês {mes_ref}" if mes_ref else "")
            }
        
        # Montar resposta estruturada
        return {
            "success": True,
            "colaborador": {
                "cod_usuario": resultado.cod_usuario,
                "nome": resultado.nome,
                "email": resultado.email,
                "cpf": resultado.cpf,
                "equipe": resultado.equipe,
                "ramal": resultado.ramal,
                "username": resultado.username
            },
            "nps_data": {
                "nps": float(resultado.nps) if resultado.nps else None,
                "qtd_detrator": resultado.qtd_detrator or 0,
                "qtd_neutro": resultado.qtd_neutro or 0,
                "qtd_promotor": resultado.qtd_promotor or 0,
                "qtd_total": resultado.qtd_tt or 0,
                "mes_referencia": resultado.mes.strftime("%Y-%m-%d") if resultado.mes else None,
                "distribuicao_notas": {
                    "nota_1": resultado.nota_1 or 0,
                    "nota_2": resultado.nota_2 or 0,
                    "nota_3": resultado.nota_3 or 0,
                    "nota_4": resultado.nota_4 or 0,
                    "nota_5": resultado.nota_5 or 0
                },
                "percentuais": {
                    "detratores": round((resultado.qtd_detrator or 0) / (resultado.qtd_tt or 1) * 100, 2) if resultado.qtd_tt else 0,
                    "neutros": round((resultado.qtd_neutro or 0) / (resultado.qtd_tt or 1) * 100, 2) if resultado.qtd_tt else 0,
                    "promotores": round((resultado.qtd_promotor or 0) / (resultado.qtd_tt or 1) * 100, 2) if resultado.qtd_tt else 0
                }
            },
            "message": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar dados de NPS: {str(e)}"
        )


@router.get("/historico/{cod_usuario}")
def get_historico_nps(
    cod_usuario: int,
    limite: int = 12,
    db: Session = Depends(get_db)
):
    """
    📊 Retorna o histórico de NPS do colaborador
    
    Busca os últimos N meses de NPS do colaborador.
    
    Args:
        cod_usuario: Código do usuário (ID Eyal)
        limite: Quantidade de meses a retornar (padrão: 12)
    """
    try:
        # Buscar histórico
        resultados = db.query(ResultadoCSAT).filter(
            ResultadoCSAT.cod_usuario == cod_usuario
        ).order_by(
            desc(ResultadoCSAT.mes)
        ).limit(limite).all()
        
        if not resultados:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum histórico de NPS encontrado para o colaborador {cod_usuario}"
            )
        
        # Formatar resposta
        historico = []
        for r in resultados:
            historico.append({
                "mes": r.mes.strftime("%Y-%m-%d") if r.mes else None,
                "nps": float(r.nps) if r.nps else None,
                "qtd_detrator": r.qtd_detrator or 0,
                "qtd_neutro": r.qtd_neutro or 0,
                "qtd_promotor": r.qtd_promotor or 0,
                "qtd_total": r.qtd_tt or 0
            })
        
        return {
            "success": True,
            "colaborador": {
                "cod_usuario": resultados[0].cod_usuario,
                "nome": resultados[0].nome
            },
            "historico": historico,
            "total_meses": len(historico)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar histórico de NPS: {str(e)}"
        )


@router.get("/equipe/{nome_equipe}")
def get_nps_equipe(
    nome_equipe: str,
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    👥 Retorna o NPS médio de uma equipe
    
    Calcula a média de NPS de todos os colaboradores da equipe.
    
    Args:
        nome_equipe: Nome da equipe
        mes_ref: Mês de referência (formato YYYY-MM). Se não fornecido, usa o mais recente.
    """
    try:
        # Construir query base
        query = db.query(ResultadoCSAT).filter(
            ResultadoCSAT.equipe.ilike(f"%{nome_equipe}%")
        )
        
        # Se mes_ref foi fornecido, filtrar pelo mês
        if mes_ref:
            try:
                data_ref = datetime.strptime(f"{mes_ref}-01", "%Y-%m-%d")
                query = query.filter(
                    func.extract('year', ResultadoCSAT.mes) == data_ref.year,
                    func.extract('month', ResultadoCSAT.mes) == data_ref.month
                )
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Formato de mês inválido: {mes_ref}. Use YYYY-MM"
                )
        
        # Buscar todos os resultados da equipe
        resultados = query.all()
        
        if not resultados:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum dado de NPS encontrado para a equipe {nome_equipe}"
            )
        
        # Calcular médias
        total_colaboradores = len(resultados)
        nps_medio = sum(float(r.nps or 0) for r in resultados) / total_colaboradores if total_colaboradores > 0 else 0
        total_detratores = sum(r.qtd_detrator or 0 for r in resultados)
        total_neutros = sum(r.qtd_neutro or 0 for r in resultados)
        total_promotores = sum(r.qtd_promotor or 0 for r in resultados)
        total_avaliacoes = sum(r.qtd_tt or 0 for r in resultados)
        
        return {
            "success": True,
            "equipe": nome_equipe,
            "mes_referencia": mes_ref,
            "resumo": {
                "nps_medio": round(nps_medio, 2),
                "total_colaboradores": total_colaboradores,
                "total_avaliacoes": total_avaliacoes,
                "qtd_detrator": total_detratores,
                "qtd_neutro": total_neutros,
                "qtd_promotor": total_promotores,
                "percentuais": {
                    "detratores": round(total_detratores / total_avaliacoes * 100, 2) if total_avaliacoes > 0 else 0,
                    "neutros": round(total_neutros / total_avaliacoes * 100, 2) if total_avaliacoes > 0 else 0,
                    "promotores": round(total_promotores / total_avaliacoes * 100, 2) if total_avaliacoes > 0 else 0
                }
            },
            "colaboradores": [
                {
                    "cod_usuario": r.cod_usuario,
                    "nome": r.nome,
                    "nps": float(r.nps) if r.nps else None,
                    "qtd_total": r.qtd_tt or 0
                }
                for r in resultados
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar NPS da equipe: {str(e)}"
        )
