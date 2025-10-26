from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.models.resultado_csat import ResultadoCSAT
from app.models.nps_unidades import NpsUnidades
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
    🌟 Retorna o NPS/CSAT de um colaborador (AGREGADO de duas tabelas)

    Busca NPS em DUAS fontes:
    1. resultadocsat - NPS individual do colaborador
    2. nps_unidades - NPS agregado de todas as unidades onde o colaborador atendeu

    Para nps_unidades, soma todos os registros do mesmo cod_usuario (independente da unidade)
    e calcula o NPS total baseado na fórmula: ((Promotores - Detratores) / Total Respondentes) * 100

    Args:
        cod_usuario: Código do usuário (ID Eyal)
        mes_ref: Mês de referência (formato YYYY-MM). Se não fornecido, usa o mais recente.

    Returns:
        Dados de NPS/CSAT do colaborador incluindo:
        - NPS agregado de ambas as tabelas
        - Quantidade de detratores, neutros e promotores
        - Detalhamento por fonte (resultadocsat e nps_unidades)
    """
    try:
        data_ref = None

        # Se mes_ref foi fornecido, converter para date
        if mes_ref:
            try:
                data_ref = datetime.strptime(f"{mes_ref}-01", "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Formato de mês inválido: {mes_ref}. Use YYYY-MM"
                )

        # ===== 1. Buscar em resultadocsat =====
        query_csat = db.query(ResultadoCSAT).filter(
            ResultadoCSAT.cod_usuario == cod_usuario
        )

        if data_ref:
            query_csat = query_csat.filter(
                func.extract('year', ResultadoCSAT.mes) == data_ref.year,
                func.extract('month', ResultadoCSAT.mes) == data_ref.month
            )

        resultado_csat = query_csat.order_by(desc(ResultadoCSAT.mes)).first()

        # ===== 2. Buscar em nps_unidades e AGREGAR =====
        query_unidades = db.query(NpsUnidades).filter(
            NpsUnidades.cod_usuario == cod_usuario
        )

        if data_ref:
            data_ref_date = data_ref.date()
            query_unidades = query_unidades.filter(NpsUnidades.mes_ref == data_ref_date)
        else:
            # Buscar o mês mais recente para este colaborador
            mes_recente = db.query(func.max(NpsUnidades.mes_ref)).filter(
                NpsUnidades.cod_usuario == cod_usuario
            ).scalar()
            if mes_recente:
                query_unidades = query_unidades.filter(NpsUnidades.mes_ref == mes_recente)

        registros_unidades = query_unidades.all()

        # Agregar valores de nps_unidades (soma de todas as unidades do colaborador)
        total_respondentes_unidades = sum(r.total_respondentes or 0 for r in registros_unidades)
        total_promotores_unidades = sum(r.total_promotores or 0 for r in registros_unidades)
        total_detratores_unidades = sum(r.total_detratores or 0 for r in registros_unidades)
        total_neutros_unidades = sum(r.total_neutros or 0 for r in registros_unidades)

        # Calcular NPS de nps_unidades
        nps_unidades = 0.0
        if total_respondentes_unidades > 0:
            nps_unidades = ((total_promotores_unidades - total_detratores_unidades) / total_respondentes_unidades) * 100

        # ===== 3. COMBINAR os dados das duas tabelas =====
        qtd_detrator_total = (resultado_csat.qtd_detrator or 0) if resultado_csat else 0
        qtd_detrator_total += total_detratores_unidades

        qtd_neutro_total = (resultado_csat.qtd_neutro or 0) if resultado_csat else 0
        qtd_neutro_total += total_neutros_unidades

        qtd_promotor_total = (resultado_csat.qtd_promotor or 0) if resultado_csat else 0
        qtd_promotor_total += total_promotores_unidades

        qtd_total = (resultado_csat.qtd_tt or 0) if resultado_csat else 0
        qtd_total += total_respondentes_unidades

        # Calcular NPS FINAL (combinado)
        nps_final = 0.0
        if qtd_total > 0:
            nps_final = ((qtd_promotor_total - qtd_detrator_total) / qtd_total) * 100

        # Se não houver dados em nenhuma tabela
        if not resultado_csat and not registros_unidades:
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
                "cod_usuario": cod_usuario,
                "nome": resultado_csat.nome if resultado_csat else (registros_unidades[0].nome_atendeu if registros_unidades else None),
                "email": resultado_csat.email if resultado_csat else None,
                "cpf": resultado_csat.cpf if resultado_csat else None,
                "equipe": resultado_csat.equipe if resultado_csat else None,
                "ramal": resultado_csat.ramal if resultado_csat else None,
                "username": resultado_csat.username if resultado_csat else None
            },
            "nps_data": {
                "nps": round(nps_final, 2),
                "qtd_detrator": qtd_detrator_total,
                "qtd_neutro": qtd_neutro_total,
                "qtd_promotor": qtd_promotor_total,
                "qtd_total": qtd_total,
                "mes_referencia": resultado_csat.mes.strftime("%Y-%m-%d") if resultado_csat and resultado_csat.mes else (
                    registros_unidades[0].mes_ref.strftime("%Y-%m-%d") if registros_unidades else mes_ref
                ),
                "distribuicao_notas": {
                    "nota_1": resultado_csat.nota_1 or 0 if resultado_csat else 0,
                    "nota_2": resultado_csat.nota_2 or 0 if resultado_csat else 0,
                    "nota_3": resultado_csat.nota_3 or 0 if resultado_csat else 0,
                    "nota_4": resultado_csat.nota_4 or 0 if resultado_csat else 0,
                    "nota_5": resultado_csat.nota_5 or 0 if resultado_csat else 0
                },
                "percentuais": {
                    "detratores": round((qtd_detrator_total / qtd_total * 100), 2) if qtd_total > 0 else 0,
                    "neutros": round((qtd_neutro_total / qtd_total * 100), 2) if qtd_total > 0 else 0,
                    "promotores": round((qtd_promotor_total / qtd_total * 100), 2) if qtd_total > 0 else 0
                },
                "detalhamento_fontes": {
                    "resultadocsat": {
                        "nps": float(resultado_csat.nps) if resultado_csat and resultado_csat.nps else 0.0,
                        "qtd_detrator": resultado_csat.qtd_detrator or 0 if resultado_csat else 0,
                        "qtd_neutro": resultado_csat.qtd_neutro or 0 if resultado_csat else 0,
                        "qtd_promotor": resultado_csat.qtd_promotor or 0 if resultado_csat else 0,
                        "qtd_total": resultado_csat.qtd_tt or 0 if resultado_csat else 0
                    },
                    "nps_unidades": {
                        "nps": round(nps_unidades, 2),
                        "qtd_detrator": total_detratores_unidades,
                        "qtd_neutro": total_neutros_unidades,
                        "qtd_promotor": total_promotores_unidades,
                        "qtd_total": total_respondentes_unidades,
                        "quantidade_unidades": len(registros_unidades)
                    }
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


@router.get("/unidade/{unidade_pagamento}")
def get_nps_unidade(
    unidade_pagamento: str,
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    🏢 Retorna o NPS agregado de uma unidade de pagamento

    Busca na tabela nps_unidades os dados agregados de NPS por unidade.
    Útil para coordenadores visualizarem o desempenho da unidade.

    Args:
        unidade_pagamento: Nome da unidade de pagamento
        mes_ref: Mês de referência (formato YYYY-MM). Se não fornecido, usa o mais recente.

    Returns:
        Dados agregados de NPS da unidade incluindo:
        - NPS calculado da unidade
        - Total de respondentes, promotores, detratores e neutros
        - Lista de colaboradores da unidade com seus NPS individuais
    """
    try:
        # Construir query base
        query = db.query(NpsUnidades).filter(
            NpsUnidades.unidade_pagamento.ilike(f"%{unidade_pagamento}%")
        )

        # Se mes_ref foi fornecido, filtrar pelo mês
        if mes_ref:
            try:
                data_ref = datetime.strptime(f"{mes_ref}-01", "%Y-%m-%d").date()
                query = query.filter(NpsUnidades.mes_ref == data_ref)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Formato de mês inválido: {mes_ref}. Use YYYY-MM"
                )
        else:
            # Buscar o mês mais recente disponível
            mes_recente = db.query(func.max(NpsUnidades.mes_ref)).filter(
                NpsUnidades.unidade_pagamento.ilike(f"%{unidade_pagamento}%")
            ).scalar()
            if mes_recente:
                query = query.filter(NpsUnidades.mes_ref == mes_recente)
                mes_ref = mes_recente.strftime("%Y-%m")

        # Buscar todos os registros da unidade
        registros = query.all()

        if not registros:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum dado de NPS encontrado para a unidade {unidade_pagamento}" +
                       (f" no mês {mes_ref}" if mes_ref else "")
            )

        # Agregar totais da unidade
        total_respondentes = sum(r.total_respondentes or 0 for r in registros)
        total_promotores = sum(r.total_promotores or 0 for r in registros)
        total_detratores = sum(r.total_detratores or 0 for r in registros)
        total_neutros = sum(r.total_neutros or 0 for r in registros)

        # Calcular NPS da unidade
        nps_unidade = 0.0
        if total_respondentes > 0:
            nps_unidade = ((total_promotores - total_detratores) / total_respondentes) * 100

        # Listar colaboradores da unidade
        colaboradores = []
        for r in registros:
            nps_colaborador = r.calcular_nps()
            colaboradores.append({
                "cod_usuario": r.cod_usuario,
                "nome_atendeu": r.nome_atendeu,
                "nps": nps_colaborador,
                "total_respondentes": r.total_respondentes or 0,
                "total_promotores": r.total_promotores or 0,
                "total_detratores": r.total_detratores or 0,
                "total_neutros": r.total_neutros or 0
            })

        # Ordenar colaboradores por NPS (maior primeiro)
        colaboradores.sort(key=lambda x: x["nps"], reverse=True)

        return {
            "success": True,
            "unidade": unidade_pagamento,
            "mes_referencia": mes_ref,
            "resumo": {
                "nps_unidade": round(nps_unidade, 2),
                "total_respondentes": total_respondentes,
                "total_promotores": total_promotores,
                "total_detratores": total_detratores,
                "total_neutros": total_neutros,
                "total_colaboradores": len(registros),
                "percentuais": {
                    "promotores": round(total_promotores / total_respondentes * 100, 2) if total_respondentes > 0 else 0,
                    "detratores": round(total_detratores / total_respondentes * 100, 2) if total_respondentes > 0 else 0,
                    "neutros": round(total_neutros / total_respondentes * 100, 2) if total_respondentes > 0 else 0
                }
            },
            "colaboradores": colaboradores
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar NPS da unidade: {str(e)}"
        )


@router.get("/diagnostico/{cod_usuario}")
def diagnostico_nps(
    cod_usuario: int,
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    🔍 Endpoint de diagnóstico para debug de NPS

    Retorna informações completas sobre:
    - Existência de dados em resultadocsat
    - Existência de dados em nps_unidades
    - Cargo e unidade do colaborador
    - Se deveria receber nps_unidade

    Útil para debug de problemas com NPS.
    """
    try:
        from app.models.metas_colaboradores import MetaColaborador
        from app.models.painel_resultados_diarios import PainelResultadosDiarios

        # Determinar mes_ref
        if mes_ref:
            try:
                data_ref = datetime.strptime(f"{mes_ref}-01", "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Formato de mês inválido: {mes_ref}. Use YYYY-MM"
                )
        else:
            # Buscar mês mais recente
            mes_recente = db.query(func.max(PainelResultadosDiarios.mes_ref)).scalar()
            if mes_recente:
                data_ref = mes_recente
                mes_ref = mes_recente.strftime("%Y-%m")
            else:
                from datetime import date
                hoje = date.today()
                data_ref = hoje.replace(day=1)
                mes_ref = data_ref.strftime("%Y-%m")

        # 1. Buscar dados do colaborador
        meta = db.query(MetaColaborador).filter(
            MetaColaborador.id_eyal == str(cod_usuario)
        ).order_by(MetaColaborador.mes_ref.desc()).first()

        painel = db.query(PainelResultadosDiarios).filter(
            PainelResultadosDiarios.id_eyal == str(cod_usuario)
        ).order_by(PainelResultadosDiarios.mes_ref.desc()).first()

        cargo = painel.cargo if painel and painel.cargo else (meta.cargo if meta and meta.cargo else None)
        unidade = painel.unidade if painel and painel.unidade else (meta.unidade if meta and meta.unidade else None)
        nome = painel.nome if painel and painel.nome else (meta.nome if meta and meta.nome else None)

        # 2. Verificar resultadocsat
        query_csat = db.query(ResultadoCSAT).filter(
            ResultadoCSAT.cod_usuario == cod_usuario,
            func.extract('year', ResultadoCSAT.mes) == data_ref.year,
            func.extract('month', ResultadoCSAT.mes) == data_ref.month
        )
        csat_row = query_csat.first()
        tem_csat = csat_row is not None

        # 3. Verificar nps_unidades
        if unidade:
            query_nps_unidade = db.query(NpsUnidades).filter(
                NpsUnidades.mes_ref == data_ref,
                NpsUnidades.unidade_pagamento.ilike(f"%{unidade}%")
            )
            nps_unidade_rows = query_nps_unidade.all()
            tem_nps_unidade = len(nps_unidade_rows) > 0
        else:
            nps_unidade_rows = []
            tem_nps_unidade = False

        # 4. Verificar se é coordenador
        eh_coordenador = cargo and "coordenador" in cargo.lower() if cargo else False
        unidade_diferente_central = unidade and "central de marca" not in unidade.lower() if unidade else False

        # 5. Buscar unidades disponíveis
        unidades_disponiveis = db.query(NpsUnidades.unidade_pagamento).filter(
            NpsUnidades.mes_ref == data_ref
        ).distinct().limit(20).all()

        # 6. Buscar meses disponíveis para este colaborador
        meses_csat = db.query(ResultadoCSAT.mes).filter(
            ResultadoCSAT.cod_usuario == cod_usuario
        ).order_by(ResultadoCSAT.mes.desc()).limit(6).all()

        return {
            "colaborador": {
                "cod_usuario": cod_usuario,
                "nome": nome,
                "cargo": cargo,
                "unidade": unidade
            },
            "mes_analise": mes_ref,
            "criterios_nps_unidade": {
                "eh_coordenador": eh_coordenador,
                "unidade_diferente_central": unidade_diferente_central,
                "deveria_receber_nps_unidade": eh_coordenador and unidade_diferente_central
            },
            "dados_encontrados": {
                "tem_registro_csat": tem_csat,
                "nps_individual": float(csat_row.nps) if csat_row and csat_row.nps else 0.0,
                "tem_dados_nps_unidade": tem_nps_unidade,
                "quantidade_registros_unidade": len(nps_unidade_rows),
                "meses_disponiveis_csat": [m[0].strftime("%Y-%m-%d") for m in meses_csat]
            },
            "debug_info": {
                "unidades_disponiveis_no_mes": [u[0] for u in unidades_disponiveis],
                "filtro_usado_unidade": f"%{unidade}%" if unidade else None,
                "mes_ref_exato": str(data_ref)
            },
            "nps_unidade_detalhes": [
                {
                    "cod_usuario": r.cod_usuario,
                    "nome_atendeu": r.nome_atendeu,
                    "total_respondentes": r.total_respondentes,
                    "nps_calculado": r.calcular_nps()
                }
                for r in nps_unidade_rows[:10]  # Limitar a 10 para não sobrecarregar
            ] if nps_unidade_rows else []
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao executar diagnóstico: {str(e)}"
        )
