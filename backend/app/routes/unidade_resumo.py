from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta, date
import calendar
import traceback
from app.database import get_db
from app.models.painel_resultados_diarios import PainelResultadosDiarios
from app.models.metas_colaboradores import MetaColaborador
from app.models.resultado_csat import ResultadoCSAT
from app.models.nps_unidades import NpsUnidades
from sqlalchemy import func, text

router = APIRouter(
    prefix="/realizado/unidade",
    tags=["Realizado/Unidade"]
)


def calcular_dias_trabalhados(data_inicio: date, data_fim: date) -> float:
    """Calcula dias trabalhados considerando segunda a sexta (1 dia) e sábado (0.5 dia)"""
    dias_trabalhados = 0
    data_atual = data_inicio
    if data_fim < data_inicio:
        return 0.0
    while data_atual <= data_fim:
        dia_semana = data_atual.weekday()
        if 0 <= dia_semana <= 4:  # Segunda a sexta
            dias_trabalhados += 1
        elif dia_semana == 5:  # Sábado
            dias_trabalhados += 0.5
        data_atual += timedelta(days=1)
    return dias_trabalhados


@router.get("/diagnostico/{unidade}")
def diagnostico_unidade(
    unidade: str,
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    🔍 Endpoint de diagnóstico para verificar dados da unidade

    Retorna informações detalhadas sobre:
    - Colaboradores encontrados na unidade
    - Metas individuais e total
    - Realizado individual e total
    - Fontes de NPS
    """
    try:
        # Determinar mes_ref
        mes_ref_dt = None
        if mes_ref:
            try:
                mes_ref_dt = datetime.strptime(str(mes_ref)[:10], "%Y-%m-%d").date()
            except:
                try:
                    mes_ref_dt = datetime.strptime(f"{mes_ref}-01", "%Y-%m-%d").date()
                except:
                    pass

        if not mes_ref_dt:
            mes_recente_meta = db.query(MetaColaborador.mes_ref).order_by(
                MetaColaborador.mes_ref.desc()
            ).first()
            if mes_recente_meta:
                mes_ref_dt = mes_recente_meta.mes_ref
            else:
                mes_ref_dt = datetime.now().date().replace(day=1)

        print(f"\n{'='*60}")
        print(f"🔍 DIAGNÓSTICO DA UNIDADE: {unidade}")
        print(f"📅 Mês de referência: {mes_ref_dt}")
        print(f"{'='*60}\n")

        # 1. Buscar colaboradores da unidade
        colaboradores = db.query(
            MetaColaborador.id_eyal,
            MetaColaborador.nome,
            MetaColaborador.cargo,
            MetaColaborador.meta_final,
            MetaColaborador.meta_diaria
        ).filter(
            MetaColaborador.unidade.ilike(f"%{unidade}%"),
            MetaColaborador.mes_ref == mes_ref_dt
        ).all()

        print(f"👥 COLABORADORES ENCONTRADOS: {len(colaboradores)}")
        print(f"{'-'*60}")

        meta_total_calc = 0
        colaboradores_lista = []

        for colab in colaboradores:
            meta_total_calc += (colab.meta_final or 0)
            print(f"  • {colab.nome} (ID: {colab.id_eyal})")
            print(f"    Cargo: {colab.cargo}")
            print(f"    Meta: R$ {colab.meta_final or 0:,.2f}")
            print(f"    Meta Diária: R$ {colab.meta_diaria or 0:,.2f}")

            colaboradores_lista.append({
                "id_eyal": colab.id_eyal,
                "nome": colab.nome,
                "cargo": colab.cargo,
                "meta_final": float(colab.meta_final or 0),
                "meta_diaria": float(colab.meta_diaria or 0)
            })

        print(f"\n💰 META TOTAL CALCULADA: R$ {meta_total_calc:,.2f}\n")

        # 2. Buscar realizado (última carga)
        latest_carga = db.query(
            func.max(PainelResultadosDiarios.data_carga)
        ).filter(
            PainelResultadosDiarios.unidade.ilike(f"%{unidade}%"),
            PainelResultadosDiarios.mes_ref == mes_ref_dt
        ).scalar()

        print(f"📊 DADOS DE REALIZADO")
        print(f"{'-'*60}")
        print(f"  Última carga: {latest_carga}")

        realizados_lista = []
        realizado_total_calc = 0

        if latest_carga:
            realizados = db.query(
                PainelResultadosDiarios.id_eyal,
                PainelResultadosDiarios.nome,
                PainelResultadosDiarios.realizado_final
            ).filter(
                PainelResultadosDiarios.unidade.ilike(f"%{unidade}%"),
                PainelResultadosDiarios.mes_ref == mes_ref_dt,
                PainelResultadosDiarios.data_carga == latest_carga
            ).all()

            for real in realizados:
                realizado_total_calc += (real.realizado_final or 0)
                print(f"  • {real.nome} (ID: {real.id_eyal})")
                print(f"    Realizado: R$ {real.realizado_final or 0:,.2f}")

                realizados_lista.append({
                    "id_eyal": real.id_eyal,
                    "nome": real.nome,
                    "realizado_final": float(real.realizado_final or 0)
                })

        print(f"\n✅ REALIZADO TOTAL: R$ {realizado_total_calc:,.2f}\n")

        # 3. Verificar NPS - ResultadoCSAT
        ids_colaboradores = [int(c.id_eyal) for c in colaboradores if c.id_eyal]

        print(f"⭐ NPS - RESULTADOCSAT")
        print(f"{'-'*60}")

        if ids_colaboradores:
            nps_csat = db.query(
                ResultadoCSAT.cod_usuario,
                ResultadoCSAT.nome,
                ResultadoCSAT.nps,
                ResultadoCSAT.qtd_detrator,
                ResultadoCSAT.qtd_neutro,
                ResultadoCSAT.qtd_promotor,
                ResultadoCSAT.qtd_tt
            ).filter(
                ResultadoCSAT.cod_usuario.in_(ids_colaboradores),
                func.extract('year', ResultadoCSAT.mes) == mes_ref_dt.year,
                func.extract('month', ResultadoCSAT.mes) == mes_ref_dt.month
            ).all()

            total_csat_detratores = 0
            total_csat_neutros = 0
            total_csat_promotores = 0
            total_csat_respondentes = 0

            for nps in nps_csat:
                total_csat_detratores += (nps.qtd_detrator or 0)
                total_csat_neutros += (nps.qtd_neutro or 0)
                total_csat_promotores += (nps.qtd_promotor or 0)
                total_csat_respondentes += (nps.qtd_tt or 0)

                print(f"  • {nps.nome} (ID: {nps.cod_usuario})")
                print(f"    NPS: {nps.nps}")
                print(f"    Promotores: {nps.qtd_promotor} | Neutros: {nps.qtd_neutro} | Detratores: {nps.qtd_detrator}")
                print(f"    Total: {nps.qtd_tt}")

            print(f"\n  📊 TOTAIS RESULTADOCSAT:")
            print(f"    Respondentes: {total_csat_respondentes}")
            print(f"    Promotores: {total_csat_promotores}")
            print(f"    Detratores: {total_csat_detratores}")
            print(f"    Neutros: {total_csat_neutros}")

        # 4. Verificar NPS - nps_unidades
        print(f"\n🏢 NPS - NPS_UNIDADES")
        print(f"{'-'*60}")

        nps_unidades_rows = db.query(
            NpsUnidades.cod_usuario,
            NpsUnidades.nome_atendeu,
            NpsUnidades.unidade_pagamento,
            NpsUnidades.total_detratores,
            NpsUnidades.total_neutros,
            NpsUnidades.total_promotores,
            NpsUnidades.total_respondentes
        ).filter(
            NpsUnidades.mes_ref == mes_ref_dt,
            NpsUnidades.unidade_pagamento.ilike(f"%{unidade}%")
        ).all()

        total_unid_detratores = 0
        total_unid_neutros = 0
        total_unid_promotores = 0
        total_unid_respondentes = 0

        for nps_u in nps_unidades_rows:
            total_unid_detratores += (nps_u.total_detratores or 0)
            total_unid_neutros += (nps_u.total_neutros or 0)
            total_unid_promotores += (nps_u.total_promotores or 0)
            total_unid_respondentes += (nps_u.total_respondentes or 0)

            print(f"  • {nps_u.nome_atendeu} (ID: {nps_u.cod_usuario})")
            print(f"    Unidade Pagamento: {nps_u.unidade_pagamento}")
            print(f"    Promotores: {nps_u.total_promotores} | Neutros: {nps_u.total_neutros} | Detratores: {nps_u.total_detratores}")
            print(f"    Total: {nps_u.total_respondentes}")

        print(f"\n  📊 TOTAIS NPS_UNIDADES:")
        print(f"    Respondentes: {total_unid_respondentes}")
        print(f"    Promotores: {total_unid_promotores}")
        print(f"    Detratores: {total_unid_detratores}")
        print(f"    Neutros: {total_unid_neutros}")

        # 5. Calcular NPS agregado
        total_respondentes = total_csat_respondentes + total_unid_respondentes
        total_promotores = total_csat_promotores + total_unid_promotores
        total_detratores = total_csat_detratores + total_unid_detratores

        nps_final = 0
        if total_respondentes > 0:
            nps_final = ((total_promotores - total_detratores) / total_respondentes) * 100

        print(f"\n🎯 NPS AGREGADO FINAL:")
        print(f"{'-'*60}")
        print(f"  Total Respondentes: {total_respondentes}")
        print(f"  Total Promotores: {total_promotores}")
        print(f"  Total Detratores: {total_detratores}")
        print(f"  NPS Calculado: {nps_final:.2f}")
        print(f"{'='*60}\n")

        return {
            "unidade": unidade,
            "mes_ref": str(mes_ref_dt),
            "resumo": {
                "total_colaboradores": len(colaboradores),
                "meta_total": round(meta_total_calc, 2),
                "realizado_total": round(realizado_total_calc, 2),
                "nps_agregado": round(nps_final, 2)
            },
            "colaboradores": colaboradores_lista,
            "realizados": realizados_lista,
            "nps_detalhado": {
                "resultadocsat": {
                    "respondentes": total_csat_respondentes,
                    "promotores": total_csat_promotores,
                    "detratores": total_csat_detratores,
                    "neutros": total_csat_neutros
                },
                "nps_unidades": {
                    "respondentes": total_unid_respondentes,
                    "promotores": total_unid_promotores,
                    "detratores": total_unid_detratores,
                    "neutros": total_unid_neutros,
                    "registros": len(nps_unidades_rows)
                },
                "agregado": {
                    "total_respondentes": total_respondentes,
                    "total_promotores": total_promotores,
                    "total_detratores": total_detratores,
                    "nps": round(nps_final, 2)
                }
            }
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro no diagnóstico: {str(e)}")


@router.get("/resumo-rapido/{unidade}")
def get_resumo_rapido_unidade(
    unidade: str,
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    🏢 Retorna um resumo rápido consolidado da UNIDADE

    Agrega dados de todos os colaboradores da unidade e calcula:
    - Meta total da unidade
    - Realizado total
    - NPS agregado (de todas as fontes: resultadocsat + nps_unidades)
    - Projeção de atingimento
    - Saldo

    Args:
        unidade: Nome da unidade (ex: "PELOTAS", "URUGUAIANA")
        mes_ref: Mês de referência (formato YYYY-MM-DD ou YYYY-MM). Se não fornecido, usa o mais recente.

    Returns:
        Resumo consolidado da unidade com KPIs agregados
    """
    try:
        # 1) Determinar mes_ref
        mes_ref_dt = None
        if mes_ref:
            try:
                # Tentar formato YYYY-MM-DD
                mes_ref_dt = datetime.strptime(str(mes_ref)[:10], "%Y-%m-%d").date()
            except:
                try:
                    # Tentar formato YYYY-MM
                    mes_ref_dt = datetime.strptime(f"{mes_ref}-01", "%Y-%m-%d").date()
                except:
                    pass

        if not mes_ref_dt:
            hoje = datetime.now().date()
            mes_ref_dt = hoje.replace(day=1)
            mes_ref = mes_ref_dt.isoformat()

        # Converter para formato YYYY-MM-DD para as queries
        data_ref = mes_ref_dt.strftime("%Y-%m-%d")

        print(f"📍 [RESUMO UNIDADE] Unidade: {unidade} | Mês: {data_ref}")

        # 2) Buscar META da unidade - MESMA FONTE DO DASHBOARD
        # Tabela: rh_homologacao.metas_unidade
        query_meta = text("""
            SELECT valor_meta
            FROM rh_homologacao.metas_unidade
            WHERE mes_ref = :data_ref
            AND TRIM(unidade) ILIKE :unidade_pattern
            LIMIT 1
        """)

        result_meta = db.execute(query_meta, {
            "data_ref": data_ref,
            "unidade_pattern": f"%{unidade}%"
        }).fetchone()

        meta_total_unidade = float(result_meta.valor_meta) if result_meta and result_meta.valor_meta else 0.0

        print(f"📊 [RESUMO UNIDADE] Meta Total: {meta_total_unidade:.2f} (fonte: metas_unidade)")

        # 3) Buscar REALIZADO da unidade - MESMA FONTE DO DASHBOARD
        # Tabela: rh_homologacao.realizado_colaborador
        query_realizado = text("""
            SELECT SUM(total_realizado) as realizado
            FROM rh_homologacao.realizado_colaborador
            WHERE mes_ref = :data_ref
            AND TRIM(unidade) ILIKE :unidade_pattern
        """)

        result_realizado = db.execute(query_realizado, {
            "data_ref": data_ref,
            "unidade_pattern": f"%{unidade}%"
        }).fetchone()

        realizado_total_unidade = float(result_realizado.realizado) if result_realizado and result_realizado.realizado else 0.0

        print(f"✅ [RESUMO UNIDADE] Realizado Total: {realizado_total_unidade:.2f} (fonte: realizado_colaborador)")

        # Meta diária (calcular baseado na meta total)
        hoje = datetime.now().date()
        if hoje.year == mes_ref_dt.year and hoje.month == mes_ref_dt.month:
            primeiro_dia_mes = mes_ref_dt
            _, ultimo_dia_num = calendar.monthrange(mes_ref_dt.year, mes_ref_dt.month)
            ultimo_dia_mes = mes_ref_dt.replace(day=ultimo_dia_num)
            dias_totais_mes = calcular_dias_trabalhados(primeiro_dia_mes, ultimo_dia_mes)
            meta_diaria_media = meta_total_unidade / dias_totais_mes if dias_totais_mes > 0 else 0
        else:
            meta_diaria_media = 0.0

        # 4) Calcular DIAS TRABALHADOS e PROJEÇÃO
        hoje = datetime.now().date()
        dias_trabalhados_ate_ontem = 0
        dias_totais_mes = 0
        producao_dia_media = 0.0
        previsao_atingimento = 0.0
        percentual_projetado = 0.0

        if hoje.year == mes_ref_dt.year and hoje.month == mes_ref_dt.month:
            # Mês atual - calcular projeção
            ontem = hoje - timedelta(days=1)
            primeiro_dia_mes = hoje.replace(day=1)
            _, ultimo_dia_num = calendar.monthrange(hoje.year, hoje.month)
            ultimo_dia_mes = hoje.replace(day=ultimo_dia_num)

            dias_trabalhados_ate_ontem = calcular_dias_trabalhados(primeiro_dia_mes, ontem)
            dias_totais_mes = calcular_dias_trabalhados(primeiro_dia_mes, ultimo_dia_mes)

            if dias_trabalhados_ate_ontem > 0 and meta_total_unidade > 0:
                producao_dia_media = realizado_total_unidade / dias_trabalhados_ate_ontem
                previsao_atingimento = producao_dia_media * dias_totais_mes
                percentual_projetado = (previsao_atingimento / meta_total_unidade) * 100
        else:
            # Mês fechado - usar realizado como previsão
            previsao_atingimento = realizado_total_unidade
            if meta_total_unidade > 0:
                percentual_projetado = (realizado_total_unidade / meta_total_unidade) * 100

        print(f"📈 [RESUMO UNIDADE] Projeção: {previsao_atingimento:.2f} ({percentual_projetado:.2f}%)")

        # 5) Calcular NPS AGREGADO da UNIDADE (de todas as fontes)
        nps_unidade_agregado = 0.0

        try:
            # 5.1) Buscar TODOS os colaboradores da unidade
            colaboradores_unidade = db.query(MetaColaborador.id_eyal).filter(
                MetaColaborador.unidade.ilike(f"%{unidade}%"),
                MetaColaborador.mes_ref == mes_ref_dt
            ).distinct().all()

            ids_colaboradores = [int(c.id_eyal) for c in colaboradores_unidade if c.id_eyal]

            print(f"👥 [RESUMO UNIDADE] Total de colaboradores: {len(ids_colaboradores)}")

            # 5.2) Agregar NPS de ResultadoCSAT (todos os colaboradores da unidade)
            total_detratores_csat = 0
            total_neutros_csat = 0
            total_promotores_csat = 0
            total_respondentes_csat = 0

            if ids_colaboradores:
                # Buscar dados agregados de resultadocsat
                resultado_csat_agg = db.query(
                    func.sum(ResultadoCSAT.qtd_detrator),
                    func.sum(ResultadoCSAT.qtd_neutro),
                    func.sum(ResultadoCSAT.qtd_promotor),
                    func.sum(ResultadoCSAT.qtd_tt)
                ).filter(
                    ResultadoCSAT.cod_usuario.in_(ids_colaboradores),
                    func.extract('year', ResultadoCSAT.mes) == mes_ref_dt.year,
                    func.extract('month', ResultadoCSAT.mes) == mes_ref_dt.month
                ).first()

                if resultado_csat_agg:
                    total_detratores_csat = int(resultado_csat_agg[0] or 0)
                    total_neutros_csat = int(resultado_csat_agg[1] or 0)
                    total_promotores_csat = int(resultado_csat_agg[2] or 0)
                    total_respondentes_csat = int(resultado_csat_agg[3] or 0)

            # 5.3) Agregar NPS de nps_unidades (todas as unidades que correspondem)
            resultado_nps_unidades_agg = db.query(
                func.sum(NpsUnidades.total_detratores),
                func.sum(NpsUnidades.total_neutros),
                func.sum(NpsUnidades.total_promotores),
                func.sum(NpsUnidades.total_respondentes)
            ).filter(
                NpsUnidades.mes_ref == mes_ref_dt,
                NpsUnidades.unidade_pagamento.ilike(f"%{unidade}%")
            ).first()

            total_detratores_unidades = int(resultado_nps_unidades_agg[0] or 0) if resultado_nps_unidades_agg else 0
            total_neutros_unidades = int(resultado_nps_unidades_agg[1] or 0) if resultado_nps_unidades_agg else 0
            total_promotores_unidades = int(resultado_nps_unidades_agg[2] or 0) if resultado_nps_unidades_agg else 0
            total_respondentes_unidades = int(resultado_nps_unidades_agg[3] or 0) if resultado_nps_unidades_agg else 0

            # 5.4) COMBINAR dados das duas fontes
            total_detratores = total_detratores_csat + total_detratores_unidades
            total_neutros = total_neutros_csat + total_neutros_unidades
            total_promotores = total_promotores_csat + total_promotores_unidades
            total_respondentes = total_respondentes_csat + total_respondentes_unidades

            # 5.5) Calcular NPS FINAL
            if total_respondentes > 0:
                nps_unidade_agregado = ((total_promotores - total_detratores) / total_respondentes) * 100

            print(f"⭐ [RESUMO UNIDADE] NPS Agregado: {nps_unidade_agregado:.2f}")
            print(f"   📊 CSAT: {total_respondentes_csat} respondentes")
            print(f"   🏢 Unidades: {total_respondentes_unidades} respondentes")
            print(f"   📈 Total: {total_respondentes} | Promotores: {total_promotores} | Detratores: {total_detratores}")

        except Exception as e:
            print(f"⚠️ [RESUMO UNIDADE] Erro ao calcular NPS: {e}")
            traceback.print_exc()

        # 6) Calcular indicadores
        saldo = realizado_total_unidade - meta_total_unidade
        percentual_atual = (realizado_total_unidade / meta_total_unidade * 100) if meta_total_unidade > 0 else 0.0

        # 7) Montar resposta
        resposta = {
            "unidade": unidade,
            "mes_ref": mes_ref,
            "meta_total": round(meta_total_unidade, 2),
            "realizado": round(realizado_total_unidade, 2),
            "saldo": round(saldo, 2),
            "producao_dia_media": round(producao_dia_media, 2),
            "meta_diaria": round(meta_diaria_media, 2),
            "previsao_atingimento": round(previsao_atingimento, 2),
            "nps": round(nps_unidade_agregado, 2),
            "percentual_atual": round(percentual_atual, 2),
            "percentual_projetado": round(percentual_projetado, 2),
            "realizado_projetado": round(previsao_atingimento, 2)
        }

        return resposta

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao obter resumo da unidade: {str(e)}"
        )
