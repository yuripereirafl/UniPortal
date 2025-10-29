from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models.realizado_colaboradores import RealizadoColaborador
from app.models.metas_colaboradores import MetaColaborador
from app.models.painel_resultados_diarios import PainelResultadosDiarios
from app.schemas.realizado import RealizadoColaborador as RealizadoSchema
from app.schemas.painel_resultados import PainelResultadosResponse
from sqlalchemy import func, and_, desc


from pydantic import BaseModel
from typing import List
from decimal import Decimal

router = APIRouter(
    prefix="/realizado",
    tags=["Realizado"]
)

# ========================================
# FUNÇÕES AUXILIARES
# ========================================

def _get_mes_mais_recente(db: Session, id_eyal: int = None) -> str:
    """
    Retorna o mês mais recente disponível na tabela realizado_colaborador.
    Se id_eyal for fornecido, busca o mês mais recente daquele colaborador.
    """
    query = db.query(func.max(RealizadoColaborador.mes_ref))
    
    if id_eyal:
        query = query.filter(RealizadoColaborador.id_eyal == id_eyal)
    
    mes_mais_recente = query.scalar()
    
    if not mes_mais_recente:
        # Fallback: buscar na tabela de metas
        query_meta = db.query(func.max(MetaColaborador.mes_ref))
        if id_eyal:
            query_meta = query_meta.filter(MetaColaborador.id_eyal == str(id_eyal))
        mes_mais_recente = query_meta.scalar()
    
    return str(mes_mais_recente) if mes_mais_recente else None


# ========================================
# NOVAS ROTAS OTIMIZADAS - PAINEL RESULTADOS
# ========================================

@router.get("/painel/{identificador}")
def get_realizado_painel(
    identificador: str, 
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    🚀 NOVA ROTA OTIMIZADA - Usa a tabela painelresultadosdiarios
    
    Retorna os dados de realizado já calculados e tratados.
    
    Args:
        identificador: ID Eyal ou CPF do colaborador
        mes_ref: Mês de referência (formato YYYY-MM-DD, opcional - usa último disponível)
        
    Returns:
        Dados completos do colaborador com realizado individual e final já calculados
    """
    try:
        # Construir query base
        query = db.query(PainelResultadosDiarios)
        
        # Filtrar por ID Eyal ou CPF
        if len(identificador) == 11 or len(identificador) == 14:  # CPF
            query = query.filter(PainelResultadosDiarios.cpf == identificador)
        else:  # ID Eyal
            query = query.filter(PainelResultadosDiarios.id_eyal == identificador)
        
        # Se não especificou mês, pegar o mais recente
        if not mes_ref:
            # Buscar a data de carga mais recente
            subquery = db.query(
                func.max(PainelResultadosDiarios.data_carga)
            ).scalar_subquery()
            
            query = query.filter(PainelResultadosDiarios.data_carga == subquery)
        else:
            # Usar mês especificado
            query = query.filter(PainelResultadosDiarios.mes_ref == mes_ref)
            # Pegar a carga mais recente desse mês
            subquery = db.query(
                func.max(PainelResultadosDiarios.data_carga)
            ).filter(PainelResultadosDiarios.mes_ref == mes_ref).scalar_subquery()
            query = query.filter(PainelResultadosDiarios.data_carga == subquery)
        
        # Executar query
        resultado = query.first()
        
        if not resultado:
            raise HTTPException(
                status_code=404, 
                detail=f"Dados não encontrados para o colaborador {identificador}"
            )
        
        # Buscar meta do colaborador
        meta_colaborador = db.query(MetaColaborador).filter(
            MetaColaborador.id_eyal == resultado.id_eyal
        ).first()
        
        meta_final = float(meta_colaborador.meta_final) if meta_colaborador and meta_colaborador.meta_final else 0
        realizado_final = float(resultado.realizado_final or 0)
        percentual_atingido = (realizado_final / meta_final * 100) if meta_final > 0 else 0
        
        # Montar resposta estruturada
        return {
            "colaborador": {
                "id_eyal": resultado.id_eyal,
                "cpf": resultado.cpf,
                "nome": resultado.nome,
                "cargo": resultado.cargo,
                "nivel": resultado.nivel,
                "unidade": resultado.unidade,
                "lider_direto": resultado.lider_direto,
                "meta_final": meta_final
            },
            "realizado": {
                "realizado_individual": float(resultado.realizado_individual or 0),
                "realizado_final": realizado_final,
                "percentual_atingido": round(percentual_atingido, 2),
                "mes_referencia": str(resultado.mes_ref),
                "data_carga": str(resultado.data_carga)
            },
            "metadata": {
                "fonte": "painelresultadosdiarios",
                "tipo_calculo": "Pré-calculado com regras de negócio aplicadas",
                "observacao": "realizado_final já inclui regras de liderança e equipe"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar dados do painel: {str(e)}"
        )


@router.get("/painel/dia-anterior/{identificador}")
def get_producao_dia_anterior(
    identificador: str,
    db: Session = Depends(get_db)
):
    """
    📅 Produção do Dia Anterior (D-1)
    
    Retorna a produção ESPECÍFICA do dia anterior (ontem).
    Calcula: Realizado até D-1 - Realizado até D-2
    
    Isso mostra quanto foi produzido APENAS no dia de ontem.
    
    Args:
        identificador: ID Eyal ou CPF do colaborador
        
    Returns:
        Produção líquida do dia anterior (D-1 - D-2)
    """
    try:
        from datetime import datetime, timedelta
        
        print(f"=== Calculando produção D-1 para {identificador} ===")
        
        # Construir query base
        base_query = db.query(PainelResultadosDiarios)
        
        # Filtrar por ID Eyal ou CPF
        if len(identificador) == 11 or len(identificador) == 14:  # CPF
            base_query = base_query.filter(PainelResultadosDiarios.cpf == identificador)
        else:  # ID Eyal
            base_query = base_query.filter(PainelResultadosDiarios.id_eyal == identificador)
        
        # Buscar as 2 últimas cargas disponíveis (D-1 e D-2)
        ultimas_cargas = base_query.order_by(
            PainelResultadosDiarios.data_carga.desc()
        ).limit(2).all()
        
        if not ultimas_cargas:
            raise HTTPException(
                status_code=404,
                detail=f"Dados não encontrados para {identificador}"
            )
        
        # Separar D-1 e D-2
        realizado_d1 = ultimas_cargas[0] if len(ultimas_cargas) > 0 else None
        realizado_d2 = ultimas_cargas[1] if len(ultimas_cargas) > 1 else None
        
        if not realizado_d1:
            raise HTTPException(
                status_code=404,
                detail=f"Dados D-1 não encontrados para {identificador}"
            )
        
        # Valores acumulados
        valor_d1 = float(realizado_d1.realizado_final or 0)
        valor_d2 = float(realizado_d2.realizado_final or 0) if realizado_d2 else 0
        
        # Calcular produção do dia: D-1 - D-2
        producao_dia = valor_d1 - valor_d2
        
        print(f"Realizado até D-1 ({realizado_d1.data_carga}): {valor_d1}")
        print(f"Realizado até D-2 ({realizado_d2.data_carga if realizado_d2 else 'N/A'}): {valor_d2}")
        print(f"Produção do dia: {producao_dia}")
        
        return {
            "success": True,
            "producao_dia": {
                "valor": producao_dia,
                "data_d1": str(realizado_d1.data_carga),
                "data_d2": str(realizado_d2.data_carga) if realizado_d2 else None,
                "realizado_ate_d1": valor_d1,
                "realizado_ate_d2": valor_d2,
                "mes_ref": str(realizado_d1.mes_ref),
                "calculo": "Realizado até D-1 menos Realizado até D-2",
                "observacao": "Produção líquida do dia anterior (apenas o que foi produzido em D-1)"
            },
            "colaborador": {
                "id_eyal": realizado_d1.id_eyal,
                "nome": realizado_d1.nome,
                "cpf": realizado_d1.cpf
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar produção D-1: {str(e)}"
        )


@router.get("/painel/historico/{identificador}")
def get_historico_realizado(
    identificador: str,
    limite: int = 12,
    db: Session = Depends(get_db)
):
    """
    📊 Histórico de realizado do colaborador
    
    Retorna os últimos N meses de realizado do colaborador.
    
    Args:
        identificador: ID Eyal ou CPF
        limite: Quantidade de meses a retornar (padrão: 12)
    """
    try:
        # Construir query
        query = db.query(PainelResultadosDiarios)
        
        # Filtrar por ID ou CPF
        if len(identificador) == 11 or len(identificador) == 14:
            query = query.filter(PainelResultadosDiarios.cpf == identificador)
        else:
            query = query.filter(PainelResultadosDiarios.id_eyal == identificador)
        
        # Ordenar por mês de referência (mais recente primeiro)
        query = query.order_by(desc(PainelResultadosDiarios.mes_ref))
        
        # Limitar resultados
        resultados = query.limit(limite).all()
        
        if not resultados:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum histórico encontrado para {identificador}"
            )
        
        # Formatar resposta
        historico = []
        for r in resultados:
            historico.append({
                "mes_referencia": str(r.mes_ref),
                "realizado_individual": float(r.realizado_individual or 0),
                "realizado_final": float(r.realizado_final or 0),
                "unidade": r.unidade,
                "cargo": r.cargo,
                "data_carga": str(r.data_carga)
            })
        
        return {
            "colaborador": {
                "id_eyal": resultados[0].id_eyal,
                "nome": resultados[0].nome,
                "cpf": resultados[0].cpf
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

# ========================================
# ENDPOINT ESPECÍFICO - LISTA UNIDADE
# (Deve vir ANTES dos endpoints com path parameters)
# ========================================

@router.get("/colaborador/lista-unidade")
def get_colaboradores_lista_unidade(
    mes_ref: Optional[str] = None,
    unidade: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retorna lista detalhada de colaboradores por unidade - VERSÃO OTIMIZADA.

    Usado no Dashboard de Unidades para exibir tabela completa de colaboradores.

    Args:
        mes_ref: Mês de referência (formato YYYY-MM). Se não fornecido, usa o mês mais recente.
        unidade: Nome da unidade (opcional). Se fornecido, filtra apenas colaboradores dessa unidade.

    Returns:
        Lista de colaboradores com dados completos de meta, realizado, NPS, vendas e comissões
    """
    try:
        from app.models.resultado_csat import ResultadoCSAT
        from app.models.resultados_campanha import ResultadoCampanha

        print(f"=== [LISTA UNIDADE OTIMIZADA] Buscando colaboradores - Mês: {mes_ref}, Unidade: {unidade} ===")

        # Auto-detectar mês mais recente se não fornecido
        if not mes_ref:
            mes_recente = db.query(MetaColaborador.mes_ref).order_by(
                MetaColaborador.mes_ref.desc()
            ).first()
            if mes_recente:
                mes_ref = mes_recente.mes_ref
            else:
                raise HTTPException(status_code=404, detail="Nenhum mês de referência encontrado")

        # Converter formato YYYY-MM para YYYY-MM-01 se necessário
        if mes_ref and len(mes_ref) == 7:  # Formato YYYY-MM
            mes_ref = f"{mes_ref}-01"

        print(f"[LISTA UNIDADE] Usando mês: {mes_ref}")

        # Buscar colaboradores com meta no mês especificado
        query = db.query(MetaColaborador).filter(
            MetaColaborador.mes_ref == mes_ref
        )

        # Filtrar por unidade se fornecida
        if unidade and unidade.strip():
            query = query.filter(MetaColaborador.unidade == unidade)
            print(f"[LISTA UNIDADE] Filtrando por unidade: {unidade}")

        colaboradores_meta = query.limit(100).all()  # Limitar a 100 para evitar sobrecarga
        print(f"[LISTA UNIDADE] Encontrados {len(colaboradores_meta)} colaboradores")

        # Extrair IDs válidos
        ids_eyal = []
        meta_por_id = {}
        for meta_colab in colaboradores_meta:
            if meta_colab.id_eyal and meta_colab.id_eyal.isdigit():
                id_eyal = int(meta_colab.id_eyal)
                ids_eyal.append(id_eyal)
                meta_por_id[id_eyal] = meta_colab

        if not ids_eyal:
            return {"colaboradores": [], "total": 0, "mes_ref": mes_ref, "unidade": unidade}

        print(f"[LISTA UNIDADE] Processando {len(ids_eyal)} IDs válidos")

        # BUSCA EM BATCH - Realizado (painel)
        paineis_dict = {}
        try:
            paineis = db.query(PainelResultadosDiarios).filter(
                PainelResultadosDiarios.id_eyal.in_([str(id) for id in ids_eyal]),
                PainelResultadosDiarios.mes_ref == mes_ref
            ).all()
            for painel in paineis:
                if painel.id_eyal and painel.id_eyal.isdigit():
                    paineis_dict[int(painel.id_eyal)] = painel
            print(f"[LISTA UNIDADE] Carregados {len(paineis_dict)} painéis")
        except Exception as e:
            print(f"[LISTA UNIDADE] Erro ao carregar painéis: {e}")

        # BUSCA EM BATCH - NPS
        nps_dict = {}
        try:
            nps_results = db.query(ResultadoCSAT).filter(
                ResultadoCSAT.cod_usuario.in_(ids_eyal),
                ResultadoCSAT.mes == mes_ref
            ).all()
            for nps in nps_results:
                if nps.cod_usuario:
                    nps_dict[nps.cod_usuario] = float(nps.nps) if nps.nps else 0.0
            print(f"[LISTA UNIDADE] Carregados {len(nps_dict)} registros NPS")
        except Exception as e:
            print(f"[LISTA UNIDADE] Erro ao carregar NPS: {e}")

        # BUSCA EM BATCH - Realizados por tipo
        realizados_dict = {}
        try:
            realizados = db.query(RealizadoColaborador).filter(
                RealizadoColaborador.id_eyal.in_(ids_eyal),
                RealizadoColaborador.mes_ref == mes_ref
            ).all()
            for realizado in realizados:
                if realizado.id_eyal not in realizados_dict:
                    realizados_dict[realizado.id_eyal] = []
                realizados_dict[realizado.id_eyal].append(realizado)
            print(f"[LISTA UNIDADE] Carregados realizados de {len(realizados_dict)} colaboradores")
        except Exception as e:
            print(f"[LISTA UNIDADE] Erro ao carregar realizados: {e}")

        # BUSCA EM BATCH - Comissões
        comissoes_dict = {}
        try:
            comissoes = db.query(ResultadoCampanha).filter(
                ResultadoCampanha.id_eyal.in_([str(id) for id in ids_eyal]),
                ResultadoCampanha.mes_ref == mes_ref
            ).all()
            for comissao in comissoes:
                if comissao.id_eyal and comissao.id_eyal.isdigit():
                    comissoes_dict[int(comissao.id_eyal)] = comissao
            print(f"[LISTA UNIDADE] Carregadas {len(comissoes_dict)} comissões")
        except Exception as e:
            print(f"[LISTA UNIDADE] Erro ao carregar comissões: {e}")

        # Processar colaboradores com dados já carregados
        colaboradores_detalhados = []
        for id_eyal in ids_eyal:
            try:
                meta_colab = meta_por_id[id_eyal]

                # Realizado
                realizado_total = 0.0
                if id_eyal in paineis_dict:
                    realizado_total = float(paineis_dict[id_eyal].realizado_final or 0)

                # Calcular valores
                meta_total = float(meta_colab.meta_final or 0)
                meta_diaria = float(meta_colab.meta_diaria or 0)
                saldo = realizado_total - meta_total
                percentual_atual = (realizado_total / meta_total * 100) if meta_total > 0 else 0

                # NPS
                nps_valor = nps_dict.get(id_eyal, 0.0)

                # Vendas por categoria
                vendas_odonto = 0
                vendas_marcuz = 0
                vendas_checkup = 0

                if id_eyal in realizados_dict:
                    for realizado in realizados_dict[id_eyal]:
                        tipo = (realizado.tipo_grupo or "").upper()
                        quantidade = int(realizado.total_registros or 0)

                        if "ODONTO" in tipo:
                            vendas_odonto += quantidade
                        elif "EXAME" in tipo or "MARCUZ" in tipo:
                            vendas_marcuz += quantidade
                        elif "CHECKUP" in tipo or "CHECK" in tipo:
                            vendas_checkup += quantidade

                vendas_total = vendas_odonto + vendas_marcuz + vendas_checkup

                # Comissão
                comissao_total = 0.0
                comissao_producao = 0.0
                if id_eyal in comissoes_dict:
                    comissao = comissoes_dict[id_eyal]
                    comissao_total = float(comissao.valor_a_pagar or 0)
                    comissao_producao = float(comissao.valor_pago_producao or 0)

                # Montar objeto do colaborador
                colaborador_dados = {
                    "id_eyal": str(id_eyal),
                    "nome": meta_colab.nome,
                    "cargo": meta_colab.cargo or "Não informado",
                    "meta_total": meta_total,
                    "meta_diaria": meta_diaria,
                    "realizado": realizado_total,
                    "saldo": saldo,
                    "percentual_atual": round(percentual_atual, 2),
                    "previsao_atingimento": realizado_total,
                    "percentual_projetado": round(percentual_atual, 2),
                    "nps": round(nps_valor, 2),
                    "vendas": {
                        "odonto": vendas_odonto,
                        "marcuz": vendas_marcuz,
                        "checkup": vendas_checkup,
                        "total": vendas_total
                    },
                    "comissao": {
                        "total": comissao_total,
                        "valor_pago_producao": comissao_producao
                    }
                }

                colaboradores_detalhados.append(colaborador_dados)

            except Exception as e:
                print(f"[LISTA UNIDADE] Erro ao processar colaborador {id_eyal}: {e}")
                continue

        print(f"[LISTA UNIDADE] Retornando {len(colaboradores_detalhados)} colaboradores processados")

        return {
            "colaboradores": colaboradores_detalhados,
            "total": len(colaboradores_detalhados),
            "mes_ref": mes_ref,
            "unidade": unidade
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[LISTA UNIDADE] Erro geral: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar lista de colaboradores: {str(e)}"
        )


# ========================================
# ROTAS LEGADAS (mantidas para compatibilidade)
# ========================================


@router.get("/colaborador/{identificador}", response_model=List[RealizadoSchema])
def get_realizado_colaborador(
    identificador: int, 
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retorna os dados realizados de um colaborador com base no id_eyal.
    
    Args:
        identificador: ID Eyal do colaborador
        mes_ref: Mês de referência (formato 'YYYY-MM-DD'). Se não fornecido, retorna todos os meses.
    """
    query = db.query(RealizadoColaborador).filter(
        RealizadoColaborador.id_eyal == identificador
    )
    
    # Se mes_ref foi fornecido, filtrar por mês
    if mes_ref:
        query = query.filter(RealizadoColaborador.mes_ref == mes_ref)
    
    realizados = query.all()
    
    if not realizados:
        raise HTTPException(status_code=404, detail="Dados de 'realizado' não encontrados para o colaborador.")

    return realizados

# Rota principal do realizado com regras de negócio
@router.get("/resumo/{identificador}")
def get_resumo_colaborador(
    identificador: int, 
    mes_ref: Optional[str] = None,  # ✅ NOVO PARÂMETRO
    db: Session = Depends(get_db)
):
    """
    ROTA PRINCIPAL DO REALIZADO COM REGRAS DE NEGÓCIO
    
    Retorna um resumo com os totais realizados aplicando as regras de negócio:
    
    REGRAS DE NEGÓCIO REFINADAS:
    1. CARGOS ESPECIAIS: supervisor de atendimento, monitor, orientador -> próprio realizado + realizado dos liderados
    2. Líderes experientes -> próprio realizado + realizado de toda unidade
    3. Líderes gerais -> próprio realizado + realizado de toda unidade
    4. Senão -> apenas próprio realizado
    
    Args:
        identificador: ID Eyal do colaborador
        mes_ref: Mês de referência (formato YYYY-MM-DD). Se não informado, usa o mês mais recente.
    """
    # Se não informou mês, pegar o mais recente
    if not mes_ref:
        mes_ref = _get_mes_mais_recente(db, identificador)
        if not mes_ref:
            raise HTTPException(status_code=404, detail="Nenhum dado de realizado encontrado")
    
    print(f"--- [REALIZADO] Buscando dados para ID {identificador} no mês {mes_ref} ---")
    return _aplicar_regras_negocio_realizado(identificador, mes_ref, db)

# Rota detalhada para o resumo com regras de liderança (mantida para compatibilidade)
@router.get("/colaborador/{identificador}/resumo")
def get_resumo_colaborador_detalhado(
    identificador: int,
    mes_ref: Optional[str] = None,  # ✅ NOVO PARÂMETRO
    db: Session = Depends(get_db)
):
    """
    ROTA DETALHADA - Retorna um resumo com os totais realizados de um colaborador,
    agrupados por tipo_grupo, e um total geral.
    
    REGRAS DE NEGÓCIO REFINADAS:
    1. Líderes experientes COM liderados -> incluir liderados
    2. Líderes da Central de Marcações (cargos específicos) -> incluir toda unidade  
    3. Líderes gerais -> incluir toda unidade
    4. Senão -> apenas próprio realizado
    
    Args:
        identificador: ID Eyal do colaborador
        mes_ref: Mês de referência (formato YYYY-MM-DD). Se não informado, usa o mês mais recente.
    """
    # Se não informou mês, pegar o mais recente
    if not mes_ref:
        mes_ref = _get_mes_mais_recente(db, identificador)
        if not mes_ref:
            raise HTTPException(status_code=404, detail="Nenhum dado de realizado encontrado")
    
    print(f"--- [REALIZADO] Buscando dados para ID {identificador} no mês {mes_ref} ---")
    return _aplicar_regras_negocio_realizado(identificador, mes_ref, db)


def _aplicar_regras_negocio_realizado(identificador: int, mes_ref: str, db: Session):
    """
    FUNÇÃO CORE - Aplica as regras de negócio para cálculo do realizado
    
    REGRAS DE NEGÓCIO REFINADAS:
    1. CARGOS ESPECIAIS: supervisor de atendimento, monitor, orientador -> próprio realizado + realizado dos liderados
    2. Líderes experientes -> próprio realizado + realizado de toda unidade
    3. Líderes gerais -> próprio realizado + realizado de toda unidade
    4. Senão -> apenas próprio realizado
    
    Args:
        identificador: ID Eyal do colaborador
        mes_ref: Mês de referência (formato YYYY-MM-DD ou string)
        db: Sessão do banco de dados
    """
    
    print(f"--- [REALIZADO] Aplicando regras para ID {identificador}, mês {mes_ref} ---")
    
    # Buscar meta do colaborador NO MÊS ESPECÍFICO
    meta_colaborador = db.query(MetaColaborador).filter(
        MetaColaborador.id_eyal == str(identificador),
        MetaColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
    ).first()
    
    if not meta_colaborador:
        print(f"--- [REALIZADO] Colaborador {identificador} não encontrado nas metas do mês {mes_ref} ---")
        # Se não tem meta, busca apenas o realizado direto
        return _get_resumo_basico(identificador, mes_ref, db)
    
    # Lista de cargos de liderança geral
    cargos_lideranca_geral = [
        'gerente',
        'supervisor',
        'supervisor de atendimento', 
        'monitor',
        'orientador',
        'coordenador'
    ]
    
    # Lista de cargos específicos para CENTRAL DE MARCAÇÕES
    cargos_central_marcacoes = [
        'supervisor de atendimento',
        'monitor',
        'orientador'
    ]
    
    # Verificar se é cargo de liderança
    cargo_lower = (meta_colaborador.cargo or '').lower()
    eh_lider_geral = any(cargo in cargo_lower for cargo in cargos_lideranca_geral)
    eh_lider_central = any(cargo in cargo_lower for cargo in cargos_central_marcacoes)
    
    # Verificar se é experiente
    eh_experiente = (meta_colaborador.nivel or '').lower() == 'experiente'
    
    # Verificar unidade - usar a unidade do realizado NO MÊS, não da meta
    unidade_realizado = None
    realizados_colaborador = db.query(RealizadoColaborador).filter(
        RealizadoColaborador.id_eyal == identificador,
        RealizadoColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
    ).first()
    
    if realizados_colaborador:
        unidade_realizado = realizados_colaborador.unidade
    
    # Fallback para unidade da meta se não tiver realizado
    unidade = unidade_realizado or meta_colaborador.unidade or ''
    unidade_upper = unidade.upper()
    eh_central_marcacoes = 'CENTRAL DE MARCAÇÕES' in unidade_upper or 'CENTRAL DE MARCACOES' in unidade_upper
    
    print(f"--- [REALIZADO] Colaborador {meta_colaborador.nome} ---")
    print(f"    Cargo: '{meta_colaborador.cargo}' | Nível: '{meta_colaborador.nivel}' | Unidade Meta: '{meta_colaborador.unidade}' | Unidade Realizado: '{unidade_realizado}'")
    print(f"    É líder geral: {eh_lider_geral} | É líder central: {eh_lider_central} | É experiente: {eh_experiente}")
    print(f"    É central de marcações: {eh_central_marcacoes}")
    
    # Lógica de negócio refinada:
    if eh_lider_central:
        # CONDIÇÃO ESPECIAL: Cargos específicos (supervisor de atendimento, monitor, orientador) recebem próprio + liderados
        print(f"--- [REALIZADO] Cargo especial ({meta_colaborador.cargo}). Usando regra de liderados ---")
        return _get_resumo_com_liderados(identificador, meta_colaborador.nome, mes_ref, db)
    elif eh_lider_geral and eh_experiente:
        # Líderes experientes recebem próprio + unidade
        print(f"--- [REALIZADO] Líder experiente. Usando regra de unidade: {unidade} ---")
        return _get_resumo_por_unidade(identificador, unidade, mes_ref, db)
    elif eh_lider_geral:
        print(f"--- [REALIZADO] Líder geral. Usando regra de unidade: {unidade} ---")
        return _get_resumo_por_unidade(identificador, unidade, mes_ref, db)
    else:
        print(f"--- [REALIZADO] Colaborador normal. Usando regra básica ---")
        return _get_resumo_basico(identificador, mes_ref, db)


def _get_resumo_por_unidade(identificador: int, unidade: str, mes_ref: str, db: Session):
    """
    Retorna o realizado de todos os colaboradores da mesma unidade baseado na tabela realizado_colaborador
    
    Args:
        identificador: ID Eyal do líder
        unidade: Nome da unidade
        mes_ref: Mês de referência
        db: Sessão do banco de dados
    """
    
    print(f"--- [REALIZADO] Buscando todos da unidade: '{unidade}' no mês {mes_ref} ---")
    
    # Buscar todos os IDs que têm registros na mesma unidade NO MÊS ESPECÍFICO
    colaboradores_unidade = db.query(RealizadoColaborador.id_eyal).filter(
        RealizadoColaborador.unidade == unidade,
        RealizadoColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
    ).distinct().all()
    
    # Extrair IDs únicos
    ids_unidade = [colab.id_eyal for colab in colaboradores_unidade if colab.id_eyal]
    
    print(f"--- [REALIZADO] Encontrados {len(ids_unidade)} colaboradores na unidade ---")
    print(f"--- [REALIZADO] IDs da unidade: {ids_unidade[:10]}{'...' if len(ids_unidade) > 10 else ''} ---")
    
    if not ids_unidade:
        # Fallback para apenas o colaborador atual
        return _get_resumo_basico(identificador, mes_ref, db)
    
    # Buscar realizado de todos da unidade NO MÊS ESPECÍFICO
    resumo_por_grupo = db.query(
        RealizadoColaborador.tipo_grupo,
        func.sum(RealizadoColaborador.total_realizado).label("total")
    ).filter(
        RealizadoColaborador.id_eyal.in_(ids_unidade),
        RealizadoColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
    ).group_by(
        RealizadoColaborador.tipo_grupo
    ).all()

    resumo_final = {item.tipo_grupo: item.total for item in resumo_por_grupo}
    total_geral = sum(resumo_final.values())
    resumo_final["TOTAL_GERAL"] = total_geral
    resumo_final["INCLUI_UNIDADE"] = True  # Flag para indicar que inclui toda unidade
    resumo_final["QTDE_COLABORADORES_UNIDADE"] = len(ids_unidade)
    resumo_final["UNIDADE"] = unidade
    resumo_final["MES_REF"] = mes_ref  # ✅ ADICIONAR MÊS NA RESPOSTA

    if not resumo_final or total_geral == 0:
        # Fallback para apenas o colaborador atual
        return _get_resumo_basico(identificador, db)

    return resumo_final


def _get_resumo_basico(identificador: int, mes_ref: str, db: Session):
    """
    Retorna apenas o realizado do próprio colaborador NO MÊS ESPECÍFICO.
    
    Args:
        identificador: ID do colaborador
        mes_ref: Mês de referência (formato 'YYYY-MM-DD')
        db: Sessão do banco de dados
    """
    resumo_por_grupo = db.query(
        RealizadoColaborador.tipo_grupo,
        func.sum(RealizadoColaborador.total_realizado).label("total")
    ).filter(
        RealizadoColaborador.id_eyal == identificador,
        RealizadoColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
    ).group_by(
        RealizadoColaborador.tipo_grupo
    ).all()

    resumo_final = {item.tipo_grupo: item.total for item in resumo_por_grupo}
    total_geral = sum(resumo_final.values())
    resumo_final["TOTAL_GERAL"] = total_geral
    resumo_final["MES_REF"] = mes_ref  # ✅ ADICIONAR MÊS NA RESPOSTA

    if not resumo_final:
        raise HTTPException(status_code=404, detail="Dados não encontrados.")

    return resumo_final


def _get_resumo_com_liderados(identificador: int, nome_lider: str, mes_ref: str, db: Session):
    """
    Retorna o realizado do líder + realizado dos liderados NO MÊS ESPECÍFICO.
    
    Args:
        identificador: ID do colaborador líder
        nome_lider: Nome do líder direto
        mes_ref: Mês de referência (formato 'YYYY-MM-DD')
        db: Sessão do banco de dados
    """
    
    # 1. Buscar todos os liderados diretos NO MÊS ESPECÍFICO
    liderados = db.query(MetaColaborador).filter(
        MetaColaborador.lider_direto == nome_lider,
        MetaColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
    ).all()
    
    print(f"--- [REALIZADO] Encontrados {len(liderados)} liderados para {nome_lider} no mês {mes_ref} ---")
    
    # 2. Lista de IDs para buscar (líder + liderados)
    ids_para_buscar = [identificador]  # Inclui o próprio líder
    
    for liderado in liderados:
        if liderado.id_eyal and liderado.id_eyal.isdigit():
            ids_para_buscar.append(int(liderado.id_eyal))
            print(f"    Liderado: {liderado.nome} (ID: {liderado.id_eyal})")
    
    print(f"--- [REALIZADO] Buscando realizado para IDs: {ids_para_buscar} no mês {mes_ref} ---")
    
    # 3. Buscar realizado de todos (líder + liderados) NO MÊS ESPECÍFICO
    resumo_por_grupo = db.query(
        RealizadoColaborador.tipo_grupo,
        func.sum(RealizadoColaborador.total_realizado).label("total")
    ).filter(
        RealizadoColaborador.id_eyal.in_(ids_para_buscar),
        RealizadoColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
    ).group_by(
        RealizadoColaborador.tipo_grupo
    ).all()

    resumo_final = {item.tipo_grupo: item.total for item in resumo_por_grupo}
    total_geral = sum(resumo_final.values())
    resumo_final["TOTAL_GERAL"] = total_geral
    resumo_final["INCLUI_LIDERADOS"] = True  # Flag para indicar que inclui liderados
    resumo_final["QTDE_LIDERADOS"] = len(liderados)
    resumo_final["MES_REF"] = mes_ref  # ✅ ADICIONAR MÊS NA RESPOSTA

    if not resumo_final or total_geral == 0:
        raise HTTPException(status_code=404, detail="Dados não encontrados.")

    return resumo_final


# Rota original mantida para compatibilidade
@router.get("/colaborador/{identificador}/resumo-original")
def get_resumo_colaborador_original(
    identificador: int, 
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retorna um resumo com os totais realizados APENAS do colaborador,
    sem aplicar regras de liderança (rota original).
    
    Args:
        identificador: ID do colaborador
        mes_ref: Mês de referência (formato 'YYYY-MM-DD'). Se não fornecido, usa o mês mais recente.
    """
    if not mes_ref:
        mes_ref = _get_mes_mais_recente(db, identificador)
    
    return _get_resumo_basico(identificador, mes_ref, db)

# 1. Crie um novo Schema para a resposta da nova rota.
#    Isso define como será o JSON de saída.
class RealizadoUnidadeSchema(BaseModel):
    unidade: str
    total_realizado: float

    class Config:
        from_attributes = True # Permite que o Pydantic leia dados de objetos SQLAlchemy

# 2. Adicione a nova rota ao seu router existente.
@router.get("/unidade", response_model=List[RealizadoUnidadeSchema])
def get_realizado_por_unidade(
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retorna a soma do total realizado para todos os colaboradores,
    agrupado por unidade NO MÊS ESPECÍFICO.
    
    Args:
        mes_ref: Mês de referência (formato 'YYYY-MM-DD'). Se não fornecido, usa o mês mais recente.
    """
    # Auto-detectar mês mais recente se não fornecido
    if not mes_ref:
        mes_recente = db.query(RealizadoColaborador.mes_ref).order_by(
            RealizadoColaborador.mes_ref.desc()
        ).first()
        if mes_recente:
            mes_ref = mes_recente.mes_ref
        else:
            raise HTTPException(status_code=404, detail="Nenhum mês de referência encontrado")
    
    # A query com SQLAlchemy para agrupar por 'unidade' e somar 'total_realizado' NO MÊS ESPECÍFICO
    realizado_agrupado = db.query(
        RealizadoColaborador.unidade,
        func.sum(RealizadoColaborador.total_realizado).label("total_realizado")
    ).filter(
        RealizadoColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
    ).group_by(
        RealizadoColaborador.unidade
    ).order_by(
        RealizadoColaborador.unidade
    ).all()

    # Se a consulta não retornar nada, lança um erro 404
    if not realizado_agrupado:
        raise HTTPException(status_code=404, detail="Nenhum dado de realizado encontrado.")

    # Retorna a lista de resultados. O FastAPI fará a conversão para o formato JSON.
    return realizado_agrupado

@router.get("/unidade/{nome_unidade}", response_model=RealizadoUnidadeSchema)
def get_realizado_por_unidade_especifica(
    nome_unidade: str, 
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Retorna a SOMA do total realizado para todos os colaboradores
    de UMA unidade específica NO MÊS ESPECÍFICO.
    
    Args:
        nome_unidade: Nome da unidade
        mes_ref: Mês de referência (formato 'YYYY-MM-DD'). Se não fornecido, usa o mês mais recente.
    """
    # Auto-detectar mês mais recente se não fornecido
    if not mes_ref:
        mes_recente = db.query(RealizadoColaborador.mes_ref).order_by(
            RealizadoColaborador.mes_ref.desc()
        ).first()
        if mes_recente:
            mes_ref = mes_recente.mes_ref
        else:
            raise HTTPException(status_code=404, detail="Nenhum mês de referência encontrado")
    
    # A query agora soma 'total_realizado' e filtra pela unidade E MÊS ESPECÍFICO
    soma_total = db.query(
        func.sum(RealizadoColaborador.total_realizado)
    ).filter(
        RealizadoColaborador.unidade == nome_unidade,
        RealizadoColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
    ).scalar()

    # Se a unidade não existir ou não tiver registros, a soma será None.
    if soma_total is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Nenhum dado de 'realizado' encontrado para a unidade: {nome_unidade} no mês {mes_ref}"
        )

    # Retorna um dicionário que corresponde ao schema 'RealizadoUnidadeSchema'.
    return {"unidade": nome_unidade, "total_realizado": soma_total}


# === NOVA ROTA: RELATÓRIO RESUMO DAS METAS ===
@router.get("/relatorio/resumo-metas")
def get_relatorio_resumo_metas(
    mes_ref: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    RELATÓRIO RESUMO DAS METAS - Retorna estrutura completa como no Excel
    
    Args:
        mes_ref: Mês de referência (formato 'YYYY-MM-DD'). Se não fornecido, usa o mês mais recente disponível.
    
    Retorna:
    - Resumo das Metas por Unidade (seção principal)
    - Resumo Gerentes (Coordenadoras das Unidades) 
    - Resumo Coordenadores (Coordenadoras das Unidades)
    - Resumo Líderes CM (Líderes da Central de Mercações)
    
    Cada item contém: Meta, Realizado (Consultas/Exames/Odonto), %, Total Realizado, % Atingido, etc.
    """
    try:
        print("=== DEBUG: Iniciando relatório resumo metas ===")
        
        # Auto-detectar mês mais recente se não fornecido
        if not mes_ref:
            # Buscar o mês mais recente das metas
            mes_recente = db.query(MetaColaborador.mes_ref).order_by(
                MetaColaborador.mes_ref.desc()
            ).first()
            if mes_recente:
                mes_ref = mes_recente.mes_ref
                print(f"DEBUG: Usando mês mais recente: {mes_ref}")
            else:
                raise HTTPException(status_code=404, detail="Nenhum mês de referência encontrado")
        
        print(f"DEBUG: Gerando relatório para o mês: {mes_ref}")
        
        # Verificar dados básicos primeiro
        total_metas = db.query(MetaColaborador).filter(
            MetaColaborador.mes_ref == mes_ref
        ).count()
        total_realizados = db.query(RealizadoColaborador).filter(
            RealizadoColaborador.mes_ref == mes_ref
        ).count()
        print(f"DEBUG: Total metas: {total_metas}, Total realizados: {total_realizados}")
        
        # Estrutura do relatório
        relatorio = {
            "titulo": f"Resumo das Metas {mes_ref}",
            "mes_ref": mes_ref,
            "data_geracao": "2025-09-30",
            "dias_trabalhados": 22.5,
            "debug_info": {
                "total_metas": total_metas,
                "total_realizados": total_realizados
            },
            "secoes": {
                "unidades": _get_resumo_unidades(mes_ref, db),
                "gerentes": _get_resumo_gerentes(mes_ref, db), 
                "coordenadores": _get_resumo_coordenadores(mes_ref, db),
                "lideres_cm": _get_resumo_lideres_cm(mes_ref, db)
            }
        }
        
        print("=== DEBUG: Relatório gerado com sucesso ===")
        return relatorio
        
    except Exception as e:
        print(f"Erro ao gerar relatório resumo metas: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

#resumo metas
def _get_resumo_unidades(mes_ref: str, db: Session):
    """
    Retorna resumo das metas por unidade (seção principal) NO MÊS ESPECÍFICO.
    
    Args:
        mes_ref: Mês de referência (formato 'YYYY-MM-DD')
        db: Sessão do banco de dados
    """
    try:
        print(f"=== DEBUG: Iniciando _get_resumo_unidades para mês {mes_ref} ===")
        
        # Buscar todas as unidades com metas NO MÊS ESPECÍFICO
        unidades = db.query(MetaColaborador.unidade).filter(
            MetaColaborador.mes_ref == mes_ref
        ).distinct().all()
        print(f"DEBUG: Encontradas {len(unidades)} unidades distintas no mês {mes_ref}")
        
        resumo_unidades = []
        
        for unidade_row in unidades:
            unidade = unidade_row.unidade
            print(f"DEBUG: Processando unidade: '{unidade}'")
            
            if not unidade:
                print("DEBUG: Unidade vazia, pulando...")
                continue
                
            # Buscar meta total da unidade NO MÊS ESPECÍFICO
            meta_total = db.query(func.sum(MetaColaborador.meta_final)).filter(
                MetaColaborador.unidade == unidade,
                MetaColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
            ).scalar() or 0
            print(f"DEBUG: Meta total da unidade '{unidade}': {meta_total}")
            
            # Buscar realizado por tipo para esta unidade NO MÊS ESPECÍFICO
            realizados = db.query(
                RealizadoColaborador.tipo_grupo,
                func.sum(RealizadoColaborador.total_realizado).label("total")
            ).filter(
                RealizadoColaborador.unidade == unidade,
                RealizadoColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
            ).group_by(RealizadoColaborador.tipo_grupo).all()
            
            print(f"DEBUG: Encontrados {len(realizados)} tipos de realizado para unidade '{unidade}'")
            
            # Organizar realizado por tipo
            realizado_consultas = 0
            realizado_exames = 0 
            realizado_odonto = 0
            
            for realizado in realizados:
                tipo = realizado.tipo_grupo.upper() if realizado.tipo_grupo else ""
                print(f"DEBUG: Tipo: '{tipo}', Total: {realizado.total}")
                if "CONSULTA" in tipo:
                    realizado_consultas += realizado.total
                elif "EXAME" in tipo:
                    realizado_exames += realizado.total
                elif "ODONTO" in tipo:
                    realizado_odonto += realizado.total
            
            total_realizado = realizado_consultas + realizado_exames + realizado_odonto
            # Converter para float para evitar erro de tipo
            total_realizado_float = float(total_realizado) if total_realizado else 0
            meta_total_float = float(meta_total) if meta_total else 0
            percentual_atingido = (total_realizado_float / meta_total_float * 100) if meta_total_float > 0 else 0
            
            print(f"DEBUG: Totais - Consultas: {realizado_consultas}, Exames: {realizado_exames}, Odonto: {realizado_odonto}")
            print(f"DEBUG: Total realizado: {total_realizado_float}, % Atingido: {percentual_atingido}")
            
            # Calcular percentuais por tipo (corrigindo o cálculo)
            perc_consultas = 100 if realizado_consultas > 0 else 0  # % do próprio valor
            perc_exames = 100 if realizado_exames > 0 else 0
            perc_odonto = 100 if realizado_odonto > 0 else 0
            
            try:
                item_unidade = {
                    "unidade": unidade,
                    "meta": meta_total_float,
                    "realizado": {
                        "consultas": {"valor": float(realizado_consultas), "percentual": perc_consultas},
                        "exames": {"valor": float(realizado_exames), "percentual": perc_exames}, 
                        "odonto": {"valor": float(realizado_odonto), "percentual": perc_odonto}
                    },
                    "total_realizado": total_realizado_float,
                    "percentual_atingido": round(percentual_atingido, 2)
                }
                
                resumo_unidades.append(item_unidade)
                print(f"DEBUG: Adicionado item para unidade '{unidade}' com sucesso")
                
            except Exception as item_error:
                print(f"DEBUG: Erro ao criar item para unidade '{unidade}': {item_error}")
                continue
        
        print(f"=== DEBUG: Retornando {len(resumo_unidades)} unidades ===")
        return resumo_unidades
        
    except Exception as e:
        print(f"Erro ao buscar resumo unidades: {e}")
        import traceback
        traceback.print_exc()
        # Retornar lista vazia mas não fazer crash
        return []


def _get_resumo_gerentes(mes_ref: str, db: Session):
    """
    Retorna resumo dos gerentes (coordenadoras das unidades) NO MÊS ESPECÍFICO.
    
    Args:
        mes_ref: Mês de referência (formato 'YYYY-MM-DD')
        db: Sessão do banco de dados
    """
    try:
        print(f"=== DEBUG: Iniciando _get_resumo_gerentes para mês {mes_ref} ===")
        
        # Buscar colaboradores com cargo de gerente NO MÊS ESPECÍFICO
        gerentes = db.query(MetaColaborador).filter(
            MetaColaborador.cargo.ilike('%gerente%'),
            MetaColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
        ).all()
        
        print(f"DEBUG: Encontrados {len(gerentes)} gerentes no mês {mes_ref}")
        
        resumo_gerentes = []
        
        for gerente in gerentes:
            print(f"DEBUG: Processando gerente: {gerente.nome} - {gerente.cargo}")
            
            # Aplicar regras de negócio para o gerente NO MÊS ESPECÍFICO
            resultado = _aplicar_regras_negocio_realizado(int(gerente.id_eyal), mes_ref, db)
            
            item_gerente = {
                "nome": gerente.nome,
                "unidade": gerente.unidade,
                "meta": gerente.meta_final or 0,
                "resultado": resultado
            }
            
            resumo_gerentes.append(item_gerente)
            print(f"DEBUG: Adicionado gerente: {gerente.nome}")
        
        print(f"=== DEBUG: Retornando {len(resumo_gerentes)} gerentes ===")
        return resumo_gerentes
        
    except Exception as e:
        print(f"Erro ao buscar resumo gerentes: {e}")
        import traceback
        traceback.print_exc()
        return []


def _get_resumo_coordenadores(mes_ref: str, db: Session):
    """
    Retorna resumo dos coordenadores NO MÊS ESPECÍFICO.
    
    Args:
        mes_ref: Mês de referência (formato 'YYYY-MM-DD')
        db: Sessão do banco de dados
    """
    try:
        # Buscar colaboradores com cargo de coordenador NO MÊS ESPECÍFICO
        coordenadores = db.query(MetaColaborador).filter(
            MetaColaborador.cargo.ilike('%coordenador%'),
            MetaColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
        ).all()
        
        resumo_coordenadores = []
        
        for coordenador in coordenadores:
            # Aplicar regras de negócio para o coordenador NO MÊS ESPECÍFICO
            resultado = _aplicar_regras_negocio_realizado(int(coordenador.id_eyal), mes_ref, db)
            
            resumo_coordenadores.append({
                "nome": coordenador.nome,
                "unidade": coordenador.unidade,
                "meta": coordenador.meta_final or 0,
                "resultado": resultado
            })
        
        return resumo_coordenadores
        
    except Exception as e:
        print(f"Erro ao buscar resumo coordenadores: {e}")
        return []


def _get_resumo_lideres_cm(mes_ref: str, db: Session):
    """
    Retorna resumo dos líderes da Central de Mercações NO MÊS ESPECÍFICO.
    
    Args:
        mes_ref: Mês de referência (formato 'YYYY-MM-DD')
        db: Sessão do banco de dados
    """
    try:
        print(f"=== DEBUG: Iniciando _get_resumo_lideres_cm para mês {mes_ref} ===")
        
        # Buscar líderes da Central de Mercações NO MÊS ESPECÍFICO
        print("DEBUG: Buscando por cargos específicos...")
        lideres_cm = db.query(MetaColaborador).filter(
            MetaColaborador.unidade.ilike('%central%marcação%'),
            MetaColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
        ).filter(
            MetaColaborador.cargo.ilike('%supervisor%') |
            MetaColaborador.cargo.ilike('%monitor%') |
            MetaColaborador.cargo.ilike('%orientador%')
        ).all()
        
        print(f"DEBUG: Encontrados {len(lideres_cm)} líderes CM no mês {mes_ref}")
        if len(lideres_cm) == 0:
            # Tentar busca mais ampla por cargos NO MÊS ESPECÍFICO
            print("DEBUG: Tentando busca mais ampla por cargos...")
            todos_cargos_central = db.query(MetaColaborador.cargo).filter(
                MetaColaborador.unidade.ilike('%central%'),
                MetaColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
            ).distinct().all()
            
            print("DEBUG: Cargos encontrados na Central:")
            for cargo_row in todos_cargos_central[:10]:
                print(f"  - {cargo_row.cargo}")
                
            # Buscar com any supervisor, monitor, orientador NO MÊS ESPECÍFICO
            lideres_cm = db.query(MetaColaborador).filter(
                MetaColaborador.unidade.ilike('%central%'),
                MetaColaborador.mes_ref == mes_ref  # ✅ FILTRO DE MÊS
            ).filter(
                MetaColaborador.cargo.ilike('%supervisor%') |
                MetaColaborador.cargo.ilike('%monitor%') |
                MetaColaborador.cargo.ilike('%orientador%')
            ).all()
            
            print(f"DEBUG: Com busca ampla encontrados {len(lideres_cm)} líderes")
        
        resumo_lideres = []
        
        for lider in lideres_cm:
            print(f"DEBUG: Processando líder CM: {lider.nome} - {lider.cargo}")
            
            # Aplicar regras de negócio para o líder NO MÊS ESPECÍFICO
            resultado = _aplicar_regras_negocio_realizado(int(lider.id_eyal), mes_ref, db)
            
            resumo_lideres.append({
                "nome": lider.nome,
                "unidade": lider.unidade,
                "meta": lider.meta_final or 0,
                "resultado": resultado
            })
        
        print(f"=== DEBUG: Retornando {len(resumo_lideres)} líderes CM ===")
        return resumo_lideres
        
    except Exception as e:
        print(f"Erro ao buscar resumo líderes CM: {e}")
        import traceback
        traceback.print_exc()
        return []

