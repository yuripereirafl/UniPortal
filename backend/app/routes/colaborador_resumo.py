from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, date
import calendar
import traceback
from app.database import get_db # Assume que get_db() retorna a Session do PostgreSQL
from app.models.painel_resultados_diarios import PainelResultadosDiarios # Modelo SQLAlchemy
from app.models.metas_colaboradores import MetaColaborador # Modelo SQLAlchemy
from app.models.resultado_csat import ResultadoCSAT # Modelo SQLAlchemy
# <<< VERIFIQUE SE O NOME DO MODELO ESTÁ CORRETO >>>
from app.models.nps_unidades import NpsUnidades # Modelo SQLAlchemy para rh_homologacao.nps_unidades
from app.models.vendas import BaseCampanhas
from app.models.resultados_campanha import ResultadoCampanha
from app.models.pagamentos_meta import PagamentoMeta
from sqlalchemy import func, extract
from app.config import settings

router = APIRouter(
    prefix="/realizado/colaborador",
    tags=["Realizado/Resumo"]
)

# --- LÓGICA DE CÁLCULO DO VUE.JS TRADUZIDA PARA PYTHON ---
def calcular_dias_trabalhados(data_inicio: date, data_fim: date) -> float:
    dias_trabalhados = 0
    data_atual = data_inicio
    if data_fim < data_inicio: return 0.0
    while data_atual <= data_fim:
        dia_semana = data_atual.weekday()
        if 0 <= dia_semana <= 4: dias_trabalhados += 1
        elif dia_semana == 5: dias_trabalhados += 0.5
        data_atual += timedelta(days=1)
    return dias_trabalhados
# --- FIM DA LÓGICA VUE.JS ---


@router.get("/resumo-rapido/{id_eyal}")
def get_resumo_rapido_colaborador(
    id_eyal: str,
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db) # Assume Session do PostgreSQL
):
    """
    Retorna um resumo rápido para o colaborador, incluindo detalhes por unidade
    para líderes fora da Central de Marcações.
    """
    try:
        # 1) Determinar mes_ref (lógica original mantida)
        mes_ref_dt = None
        if mes_ref:
            try: mes_ref_dt = datetime.strptime(str(mes_ref)[:10], "%Y-%m-%d").date()
            except Exception: pass
        if not mes_ref_dt:
            mes_recente_meta = db.query(MetaColaborador.mes_ref).order_by(MetaColaborador.mes_ref.desc()).first()
            if mes_recente_meta:
                 mes_ref_dt = mes_recente_meta.mes_ref
                 mes_ref = mes_ref_dt.isoformat()
            else:
                 hoje = datetime.now().date()
                 mes_ref_dt = hoje.replace(day=1)
                 mes_ref = mes_ref_dt.isoformat()

        # 2) Obter registro do painel consolidado do LÍDER (para dados cadastrais e fallback)
        painel_q = db.query(PainelResultadosDiarios).filter(
            PainelResultadosDiarios.id_eyal == id_eyal,
            PainelResultadosDiarios.mes_ref == mes_ref_dt
        )
        subq = db.query(func.max(PainelResultadosDiarios.data_carga)).filter(
            PainelResultadosDiarios.id_eyal == id_eyal,
            PainelResultadosDiarios.mes_ref == mes_ref_dt
        ).scalar_subquery()
        painel_lider = painel_q.filter(PainelResultadosDiarios.data_carga == subq).first()

        # 3) Obter meta do LÍDER (para dados cadastrais e fallback)
        meta_lider = db.query(MetaColaborador).filter(
            MetaColaborador.id_eyal == id_eyal,
            MetaColaborador.mes_ref == mes_ref_dt
        ).first()
        if not meta_lider:
            meta_lider = db.query(MetaColaborador).filter(MetaColaborador.id_eyal == id_eyal).order_by(MetaColaborador.mes_ref.desc()).first()

        if not meta_lider and not painel_lider:
            raise HTTPException(status_code=404, detail=f"Colaborador com id_eyal '{id_eyal}' não encontrado ou sem dados no sistema para {mes_ref}.")

        # --- Informações básicas do colaborador (Líder) ---
        nome_lider = painel_lider.nome if painel_lider and painel_lider.nome else (meta_lider.nome if meta_lider and meta_lider.nome else "N/A")
        cargo_lider = painel_lider.cargo if painel_lider and painel_lider.cargo else (meta_lider.cargo if meta_lider and meta_lider.cargo else "")
        unidade_principal_lider = painel_lider.unidade if painel_lider and painel_lider.unidade else (meta_lider.unidade if meta_lider and meta_lider.unidade else "")
        
        # --- Lógica de Cascata de Liderança (mantida) ---
        hierarquia_lideranca: List[Dict[str, Any]] = []
        # ... (código da hierarquia) ...

        # --- Lógica de Liderança e Cálculo por Unidade ---
        desempenho_por_unidade = []
        lista_cargos_lideranca = ["coordenador", "gerente"]
        eh_lider = any(cargo in cargo_lider.lower() for cargo in lista_cargos_lideranca)
        eh_da_central = "central de marca" in unidade_principal_lider.lower()

        # Inicializar variáveis de dias trabalhados (usadas em múltiplos lugares)
        hoje = datetime.now().date()
        dias_trabalhados_ate_ontem = 0
        dias_totais_mes = 0

        # <<< AJUSTE PRINCIPAL AQUI >>>
        if eh_lider and not eh_da_central:
            print(f"INFO: {nome_lider} ({id_eyal}) é líder fora da central. Calculando desempenho por unidade...")

            # A. Buscar unidades distintas lideradas DIRETAMENTE por este líder no mês
            subordinados_unidades = db.query(MetaColaborador.unidade).filter(
                # Usa o NOME do líder para encontrar liderados diretos
                MetaColaborador.lider_direto == nome_lider,
                MetaColaborador.mes_ref == mes_ref_dt
            ).distinct().all()
            unidades_lideradas = [u[0] for u in subordinados_unidades if u[0] and "central de marca" not in u[0].lower()]

            print(f"Unidades lideradas encontradas: {unidades_lideradas}")

            # B. Calcular dias trabalhados do mês (para projeção)
            if hoje.year == mes_ref_dt.year and hoje.month == mes_ref_dt.month:
                 ontem = hoje - timedelta(days=1)
                 primeiro_dia_mes = hoje.replace(day=1)
                 _, ultimo_dia_num = calendar.monthrange(hoje.year, hoje.month)
                 ultimo_dia_mes = hoje.replace(day=ultimo_dia_num)
                 dias_trabalhados_ate_ontem = calcular_dias_trabalhados(primeiro_dia_mes, ontem)
                 dias_totais_mes = calcular_dias_trabalhados(primeiro_dia_mes, ultimo_dia_mes)


            # C. Loop para calcular desempenho de CADA unidade liderada
            for unidade_nome in unidades_lideradas:
                print(f"  Calculando para unidade: {unidade_nome}")
                
                # C.1. Calcular Meta Total da Unidade (Soma de TODOS na unidade)
                meta_unidade_total = db.query(func.sum(MetaColaborador.meta_final)).filter(
                    MetaColaborador.unidade == unidade_nome,
                    MetaColaborador.mes_ref == mes_ref_dt
                ).scalar() or 0.0
                meta_unidade_total = float(meta_unidade_total)

                # C.2. Calcular Realizado Total da Unidade (Soma de TODOS na unidade, última carga)
                latest_carga_unit = db.query(func.max(PainelResultadosDiarios.data_carga)).filter(
                    PainelResultadosDiarios.unidade == unidade_nome,
                    PainelResultadosDiarios.mes_ref == mes_ref_dt
                ).scalar()
                
                realizado_unidade_total = 0.0
                if latest_carga_unit:
                     realizado_unidade_total = db.query(func.sum(PainelResultadosDiarios.realizado_final)).filter(
                         PainelResultadosDiarios.unidade == unidade_nome,
                         PainelResultadosDiarios.mes_ref == mes_ref_dt,
                         PainelResultadosDiarios.data_carga == latest_carga_unit
                     ).scalar() or 0.0
                     realizado_unidade_total = float(realizado_unidade_total)
                
                # C.3. Calcular Percentual Projetado da Unidade
                percentual_projetado_unidade = 0.0
                previsao_atingimento_unidade = 0.0
                if hoje.year == mes_ref_dt.year and hoje.month == mes_ref_dt.month and dias_trabalhados_ate_ontem > 0 and meta_unidade_total > 0:
                    producao_dia_media_unidade = realizado_unidade_total / dias_trabalhados_ate_ontem
                    previsao_atingimento_unidade = producao_dia_media_unidade * dias_totais_mes
                    percentual_projetado_unidade = (previsao_atingimento_unidade / meta_unidade_total * 100)
                elif meta_unidade_total > 0: # Mês fechado ou sem dias trabalhados ainda
                    previsao_atingimento_unidade = realizado_unidade_total
                    percentual_projetado_unidade = (realizado_unidade_total / meta_unidade_total * 100)
                
                # C.4. Calcular NPS da Unidade (usando tabela nps_unidades)
                nps_unidade_agregado = db.query(
                    func.sum(NpsUnidades.total_respondentes),
                    func.sum(NpsUnidades.total_promotores),
                    func.sum(NpsUnidades.total_detratores)
                ).filter(
                    NpsUnidades.mes_ref == mes_ref_dt,
                    # Garante comparação case-insensitive e remove espaços extras
                    func.lower(func.trim(NpsUnidades.unidade_pagamento)) == func.lower(func.trim(unidade_nome)) 
                ).group_by(func.lower(func.trim(NpsUnidades.unidade_pagamento))).first() # Agrupa para garantir um resultado

                nps_unidade_calc = 0.0
                total_resp_unid = 0
                if nps_unidade_agregado and nps_unidade_agregado[0] is not None and nps_unidade_agregado[0] > 0:
                    total_resp_unid = nps_unidade_agregado[0]
                    total_prom_unid = nps_unidade_agregado[1] or 0
                    total_detr_unid = nps_unidade_agregado[2] or 0
                    nps_unidade_calc = round(((total_prom_unid - total_detr_unid) / total_resp_unid) * 100, 2)
                    
                print(f"  Unidade {unidade_nome}: Meta={meta_unidade_total:.2f}, Realizado={realizado_unidade_total:.2f}, Proj %={percentual_projetado_unidade:.2f}, NPS={nps_unidade_calc} (Resp: {total_resp_unid})")

                desempenho_por_unidade.append({
                    "unidade": unidade_nome,
                    "meta_total_unidade": round(meta_unidade_total, 2),
                    "realizado_unidade": round(realizado_unidade_total, 2),
                    "percentual_projetado_unidade": round(percentual_projetado_unidade, 2),
                    "nps_unidade": nps_unidade_calc
                })
        
        # --- Cálculos Consolidados do LÍDER (mantidos como antes para referência) ---
        meta_total_lider = float(meta_lider.meta_final) if meta_lider and meta_lider.meta_final else 0.0
        meta_diaria_lider = float(meta_lider.meta_diaria) if meta_lider and meta_lider.meta_diaria else 0.0
        realizado_final_lider = float(painel_lider.realizado_final) if painel_lider and painel_lider.realizado_final else 0.0

        # Calcular projeção consolidada do LÍDER (como antes)
        producao_dia_media_lider = 0
        previsao_atingimento_lider = 0
        percentual_projetado_lider = 0
        # Re-calcular dias se não foi calculado no bloco 'if eh_lider...'
        if dias_totais_mes == 0 and hoje.year == mes_ref_dt.year and hoje.month == mes_ref_dt.month:
             ontem = hoje - timedelta(days=1); primeiro_dia_mes = hoje.replace(day=1)
             _, ultimo_dia_num = calendar.monthrange(hoje.year, hoje.month); ultimo_dia_mes = hoje.replace(day=ultimo_dia_num)
             dias_trabalhados_ate_ontem = calcular_dias_trabalhados(primeiro_dia_mes, ontem)
             dias_totais_mes = calcular_dias_trabalhados(primeiro_dia_mes, ultimo_dia_mes)
             
        if dias_trabalhados_ate_ontem > 0 and meta_total_lider > 0:
             producao_dia_media_lider = realizado_final_lider / dias_trabalhados_ate_ontem
             previsao_atingimento_lider = producao_dia_media_lider * dias_totais_mes
             percentual_projetado_lider = (previsao_atingimento_lider / meta_total_lider * 100)
        elif meta_total_lider > 0:
             previsao_atingimento_lider = realizado_final_lider
             percentual_projetado_lider = (realizado_final_lider / meta_total_lider * 100)
        
        # Buscar NPS AGREGADO do colaborador (resultadocsat + nps_unidades)
        nps_colaborador_agregado = 0.0
        try:
            cod_usuario_int = int(id_eyal)

            # 1. Buscar em resultadocsat
            query_csat = db.query(ResultadoCSAT).filter(ResultadoCSAT.cod_usuario == cod_usuario_int)
            query_csat = query_csat.filter(
                func.extract('year', ResultadoCSAT.mes) == mes_ref_dt.year,
                func.extract('month', ResultadoCSAT.mes) == mes_ref_dt.month
            )
            resultado_csat = query_csat.order_by(ResultadoCSAT.mes.desc()).first()

            # 2. Buscar em nps_unidades (agregar TODAS as unidades do colaborador)
            query_unidades = db.query(NpsUnidades).filter(
                NpsUnidades.cod_usuario == cod_usuario_int,
                NpsUnidades.mes_ref == mes_ref_dt
            )
            registros_unidades = query_unidades.all()

            # Agregar valores de nps_unidades
            total_respondentes_unidades = sum(r.total_respondentes or 0 for r in registros_unidades)
            total_promotores_unidades = sum(r.total_promotores or 0 for r in registros_unidades)
            total_detratores_unidades = sum(r.total_detratores or 0 for r in registros_unidades)
            total_neutros_unidades = sum(r.total_neutros or 0 for r in registros_unidades)

            # 3. COMBINAR os dados das duas tabelas
            qtd_detrator_total = (resultado_csat.qtd_detrator or 0) if resultado_csat else 0
            qtd_detrator_total += total_detratores_unidades

            qtd_neutro_total = (resultado_csat.qtd_neutro or 0) if resultado_csat else 0
            qtd_neutro_total += total_neutros_unidades

            qtd_promotor_total = (resultado_csat.qtd_promotor or 0) if resultado_csat else 0
            qtd_promotor_total += total_promotores_unidades

            qtd_total = (resultado_csat.qtd_tt or 0) if resultado_csat else 0
            qtd_total += total_respondentes_unidades

            # 4. Calcular NPS FINAL (combinado)
            if qtd_total > 0:
                nps_colaborador_agregado = ((qtd_promotor_total - qtd_detrator_total) / qtd_total) * 100

        except Exception as e:
            print(f"Erro ao buscar NPS agregado: {e}")
            pass 

        # --- Montar Resposta Final ---
        colaborador_info = {
            "id_eyal": id_eyal,
            "nome": nome_lider,
            "cargo": cargo_lider,
            "unidade": unidade_principal_lider, # Unidade principal do líder
            "hierarquia_lideranca": hierarquia_lideranca 
        }
        
        saldo_lider = realizado_final_lider - meta_total_lider
        percentual_atual_lider = (realizado_final_lider / meta_total_lider * 100) if meta_total_lider > 0 else 0.0

        resposta = {
            "colaborador": colaborador_info,
            "mes_ref": mes_ref,
            
            # KPIs Consolidados do LÍDER (mantidos)
            "meta_total": round(meta_total_lider, 2),
            "realizado": round(realizado_final_lider, 2),
            "saldo": round(saldo_lider, 2),
            "producao_dia_media": round(producao_dia_media_lider, 2),
            "meta_diaria": round(meta_diaria_lider, 2),
            "previsao_atingimento": round(previsao_atingimento_lider, 2),
            "nps": round(nps_colaborador_agregado, 2), # NPS AGREGADO (resultadocsat + nps_unidades)
            "percentual_atual": round(percentual_atual_lider, 2),
            "percentual_projetado": round(percentual_projetado_lider, 2),
            "realizado_projetado": round(previsao_atingimento_lider, 2),
        }

        # Adicionar o detalhamento por unidade se foi calculado
        if desempenho_por_unidade:
            resposta["desempenho_por_unidade"] = desempenho_por_unidade

        return resposta

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao obter resumo rápido: {str(e)}")


def classificar_grupo(grupo_exames: str, abrev_exame: str) -> str:
    """Classifica a venda em uma categoria específica"""
    if not grupo_exames:
        grupo_exames = ""
    if not abrev_exame:
        abrev_exame = ""

    grupo_upper = grupo_exames.strip().upper()
    abrev_upper = abrev_exame.strip().upper()

    # Usar 'in' para pegar variações como "157 - ODONTO", "ODONTO", etc
    if 'ODONTO' in grupo_upper:
        return 'ODONTO'
    elif 'CHECK UP' in grupo_upper or 'CHECKUP' in grupo_upper:
        return 'CHECK UP'
    elif 'BABYCLICK' in grupo_upper or 'BABY CLICK' in grupo_upper:
        return 'BabyClick'
    elif 'DR CENTRAL' in abrev_upper or 'DR CENTRAL' in grupo_upper:
        return 'DR CENTRAL'
    else:
        return 'MARCUZ'  # Exames/Marcuz


def obter_ordem_hierarquia(cargo: str) -> int:
    """
    Retorna um número representando a ordem hierárquica do cargo.
    Menor número = maior hierarquia
    """
    cargo_upper = cargo.upper() if cargo else ""

    # Verificar em cada lista de cargos
    if any(c in cargo_upper for c in ["GERENTE"]):
        return 1
    elif any(c in cargo_upper for c in ["COORDENADOR"]):
        return 2
    elif any(c in cargo_upper for c in ["MONITOR"]):
        return 3
    elif any(c in cargo_upper for c in ["SUPERVISOR"]):
        return 4
    elif any(c in cargo_upper for c in ["ATENDENTE"]):
        return 5
    elif any(c in cargo_upper for c in ["ESTAGIÁRIO", "ESTAGIARIA"]):
        return 6
    else:
        return 99  # Cargos não reconhecidos vão pro final


@router.get("/lista-unidade")
def listar_colaboradores_unidade(
    unidade: Optional[str] = None,
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    📋 Retorna lista detalhada de TODOS os colaboradores de uma unidade
    com métricas individuais, ordenados por hierarquia de cargo.

    Retorna:
    - Nome, cargo, unidade
    - Meta total, realizado, saldo
    - Projeção de atingimento
    - NPS agregado
    - Vendas detalhadas (ODONTO, MARCUZ, CHECK-UP, DN CENTRAL, DIAGNÓSTICOS)
    - Comissão (Valor Pago Produção, Campanhas)

    Args:
        unidade: Nome da unidade (ex: "PELOTAS"). Se não fornecido, retorna todos
        mes_ref: Mês de referência (formato YYYY-MM-DD ou YYYY-MM)
    """
    try:
        # 1) Determinar mes_ref
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
            hoje = datetime.now().date()
            mes_ref_dt = hoje.replace(day=1)
            mes_ref = mes_ref_dt.isoformat()

        print(f"\n{'='*80}")
        print(f"📋 LISTANDO COLABORADORES DA UNIDADE")
        print(f"📍 Unidade: {unidade or 'TODAS'} | Mês: {mes_ref_dt}")
        print(f"{'='*80}\n")

        # 2) Buscar todos colaboradores da unidade
        query = db.query(MetaColaborador).filter(MetaColaborador.mes_ref == mes_ref_dt)

        if unidade:
            query = query.filter(MetaColaborador.unidade.ilike(f"%{unidade}%"))

        colaboradores = query.all()

        if not colaboradores:
            return {
                "unidade": unidade,
                "mes_ref": mes_ref,
                "total_colaboradores": 0,
                "colaboradores": []
            }

        print(f"👥 Total de colaboradores encontrados: {len(colaboradores)}\n")

        # 3) Calcular dias trabalhados do mês (para projeção)
        hoje = datetime.now().date()
        dias_trabalhados_ate_ontem = 0
        dias_totais_mes = 0

        if hoje.year == mes_ref_dt.year and hoje.month == mes_ref_dt.month:
            ontem = hoje - timedelta(days=1)
            primeiro_dia_mes = hoje.replace(day=1)
            _, ultimo_dia_num = calendar.monthrange(hoje.year, hoje.month)
            ultimo_dia_mes = hoje.replace(day=ultimo_dia_num)
            dias_trabalhados_ate_ontem = calcular_dias_trabalhados(primeiro_dia_mes, ontem)
            dias_totais_mes = calcular_dias_trabalhados(primeiro_dia_mes, ultimo_dia_mes)

        # 4) Processar cada colaborador
        lista_colaboradores = []

        for colab in colaboradores:
            try:
                id_eyal = colab.id_eyal
                nome = colab.nome or "N/A"
                cargo = colab.cargo or ""
                unidade_colab = colab.unidade or ""

                print(f"  📊 Processando: {nome} ({cargo})")

                # 4.1) Meta e realizado
                meta_total = float(colab.meta_final or 0)
                meta_diaria = float(colab.meta_diaria or 0)

                # Buscar realizado (última carga)
                latest_carga = db.query(func.max(PainelResultadosDiarios.data_carga)).filter(
                    PainelResultadosDiarios.id_eyal == id_eyal,
                    PainelResultadosDiarios.mes_ref == mes_ref_dt
                ).scalar()

                realizado = 0.0
                if latest_carga:
                    painel = db.query(PainelResultadosDiarios).filter(
                        PainelResultadosDiarios.id_eyal == id_eyal,
                        PainelResultadosDiarios.mes_ref == mes_ref_dt,
                        PainelResultadosDiarios.data_carga == latest_carga
                    ).first()

                    if painel:
                        realizado = float(painel.realizado_final or 0)

                # 4.2) Calcular projeção
                saldo = realizado - meta_total
                percentual_atual = (realizado / meta_total * 100) if meta_total > 0 else 0.0

                producao_dia_media = 0.0
                previsao_atingimento = 0.0
                percentual_projetado = 0.0

                if dias_trabalhados_ate_ontem > 0 and meta_total > 0:
                    producao_dia_media = realizado / dias_trabalhados_ate_ontem
                    previsao_atingimento = producao_dia_media * dias_totais_mes
                    percentual_projetado = (previsao_atingimento / meta_total * 100)
                elif meta_total > 0:
                    previsao_atingimento = realizado
                    percentual_projetado = percentual_atual

                # 4.3) Buscar NPS agregado
                nps_agregado = 0.0
                try:
                    cod_usuario_int = int(id_eyal)

                    # ResultadoCSAT
                    resultado_csat = db.query(ResultadoCSAT).filter(
                        ResultadoCSAT.cod_usuario == cod_usuario_int,
                        extract('year', ResultadoCSAT.mes) == mes_ref_dt.year,
                        extract('month', ResultadoCSAT.mes) == mes_ref_dt.month
                    ).first()

                    # NpsUnidades
                    registros_unidades = db.query(NpsUnidades).filter(
                        NpsUnidades.cod_usuario == cod_usuario_int,
                        NpsUnidades.mes_ref == mes_ref_dt
                    ).all()

                    # Agregar
                    qtd_detrator_total = (resultado_csat.qtd_detrator or 0) if resultado_csat else 0
                    qtd_detrator_total += sum(r.total_detratores or 0 for r in registros_unidades)

                    qtd_promotor_total = (resultado_csat.qtd_promotor or 0) if resultado_csat else 0
                    qtd_promotor_total += sum(r.total_promotores or 0 for r in registros_unidades)

                    qtd_total = (resultado_csat.qtd_tt or 0) if resultado_csat else 0
                    qtd_total += sum(r.total_respondentes or 0 for r in registros_unidades)

                    if qtd_total > 0:
                        nps_agregado = ((qtd_promotor_total - qtd_detrator_total) / qtd_total) * 100
                except:
                    pass

                # 4.4) Buscar vendas detalhadas
                vendas = {
                    "odonto": 0,
                    "marcuz": 0,
                    "checkup": 0,
                    "dn_central": 0,
                    "diagnosticos": 0,
                    "total": 0
                }

                try:
                    vendas_registros = db.query(BaseCampanhas).filter(
                        BaseCampanhas.cod_usuario == id_eyal,
                        extract('year', BaseCampanhas.mes) == mes_ref_dt.year,
                        extract('month', BaseCampanhas.mes) == mes_ref_dt.month
                    ).all()

                    for venda in vendas_registros:
                        # Classificar usando grupo_exames e abrev_exame
                        categoria = classificar_grupo(
                            venda.grupo_exames or "",
                            venda.abrev_exame or ""
                        )

                        # Cada registro é uma venda (quantidade = 1)
                        if categoria == 'ODONTO':
                            vendas["odonto"] += 1
                        elif categoria == 'MARCUZ':
                            vendas["marcuz"] += 1
                        elif categoria == 'CHECK UP':
                            vendas["checkup"] += 1
                        elif categoria == 'DR CENTRAL':
                            vendas["dn_central"] += 1
                        # BabyClick vai para diagnósticos
                        elif categoria == 'BabyClick':
                            vendas["diagnosticos"] += 1

                    vendas["total"] = vendas["odonto"] + vendas["marcuz"] + vendas["checkup"] + vendas["dn_central"] + vendas["diagnosticos"]
                except:
                    pass

                # 4.5) Buscar comissão
                comissao = {
                    "valor_pago_producao": 0.0,
                    "campanhas": 0.0,
                    "total": 0.0
                }

                try:
                    # Valor Pago Produção (pagamentos_meta)
                    pagamento = db.query(PagamentoMeta).filter(
                        PagamentoMeta.id_eyal == id_eyal,
                        PagamentoMeta.mes_ref == mes_ref_dt
                    ).first()

                    if pagamento:
                        comissao["valor_pago_producao"] = float(pagamento.valor_a_pagar or 0)

                    # Campanhas (resultados_campanha)
                    resultado_campanha = db.query(ResultadoCampanha).filter(
                        ResultadoCampanha.id_eyal == id_eyal,
                        ResultadoCampanha.mes_ref == mes_ref_dt
                    ).first()

                    if resultado_campanha:
                        comissao["campanhas"] = float(resultado_campanha.valor_a_pagar or 0)

                    comissao["total"] = comissao["valor_pago_producao"] + comissao["campanhas"]
                except:
                    pass

                # 4.6) Montar objeto do colaborador
                colaborador_obj = {
                    "id_eyal": id_eyal,
                    "nome": nome,
                    "cargo": cargo,
                    "unidade": unidade_colab,
                    "ordem_hierarquia": obter_ordem_hierarquia(cargo),  # Para ordenação
                    "meta_total": round(meta_total, 2),
                    "meta_diaria": round(meta_diaria, 2),
                    "realizado": round(realizado, 2),
                    "saldo": round(saldo, 2),
                    "percentual_atual": round(percentual_atual, 2),
                    "producao_dia_media": round(producao_dia_media, 2),
                    "previsao_atingimento": round(previsao_atingimento, 2),
                    "percentual_projetado": round(percentual_projetado, 2),
                    "nps": round(nps_agregado, 2),
                    "vendas": vendas,
                    "comissao": comissao
                }

                lista_colaboradores.append(colaborador_obj)

            except Exception as e:
                print(f"  ⚠️ Erro ao processar {colab.nome}: {e}")
                traceback.print_exc()
                continue

        # 5) Ordenar por hierarquia (ordem crescente = maior hierarquia primeiro)
        lista_colaboradores.sort(key=lambda x: (x["ordem_hierarquia"], x["nome"]))

        # Remover campo de ordenação antes de retornar
        for colab in lista_colaboradores:
            del colab["ordem_hierarquia"]

        print(f"\n✅ Processamento concluído: {len(lista_colaboradores)} colaboradores\n")
        print(f"{'='*80}\n")

        return {
            "unidade": unidade,
            "mes_ref": mes_ref,
            "total_colaboradores": len(lista_colaboradores),
            "colaboradores": lista_colaboradores
        }

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar colaboradores da unidade: {str(e)}"
        )