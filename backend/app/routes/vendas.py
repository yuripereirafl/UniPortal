from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

from app.dependencies import get_db
from app.models.vendas import BaseCampanhas
from app.models.metas_colaboradores import MetaColaborador
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
        return 'ORÇAMENTOS'


@router.get("/colaborador/{cod_usuario}", response_model=VendasResponse)
async def get_vendas_colaborador(
    cod_usuario: str,
    mes_ref: Optional[str] = Query(None, description="Mês de referência no formato YYYY-MM"),
    db: Session = Depends(get_db)
):
    """
    Retorna todas as vendas de um colaborador específico.
    
    REGRA DE LIDERANÇA:
    - Se o colaborador for LÍDER (supervisor, monitor, orientador, etc), 
      retorna a soma das vendas dele + vendas da sua equipe.
    """
    try:
        if mes_ref:
            try:
                mes_referencia = datetime.strptime(mes_ref, "%Y-%m").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM")
        else:
            hoje = date.today()
            mes_referencia = date(hoje.year, hoje.month, 1)
        
        # ✅ NOVO: Verificar se o colaborador é LÍDER consultando a tabela de metas
        mes_ref_str = mes_referencia.strftime("%Y-%m-01")  # Formato YYYY-MM-DD
        
        meta_colaborador = db.query(MetaColaborador).filter(
            MetaColaborador.id_eyal == cod_usuario,
            MetaColaborador.mes_ref == mes_ref_str
        ).first()
        
        # Lista de cargos de liderança (mesma lógica do endpoint de realizado)
        cargos_lideranca = [
            "supervisor de atendimento",
            "monitor",
            "orientador",
            "coordenador",
            "gerente"
        ]
        
        eh_lider = False
        nome_lider = None
        
        if meta_colaborador:
            cargo_lower = (meta_colaborador.cargo or "").lower()
            eh_lider = any(cargo in cargo_lower for cargo in cargos_lideranca)
            nome_lider = meta_colaborador.nome
         
        # Se for líder, buscar vendas dele + equipe
        if eh_lider and nome_lider:
            return await _get_vendas_com_liderados(cod_usuario, nome_lider, mes_referencia, mes_ref_str, db)
        
        # Se não for líder, retorna apenas as vendas dele (lógica original)
        
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


async def _get_vendas_com_liderados(
    cod_usuario_lider: str, 
    nome_lider: str, 
    mes_referencia: date,
    mes_ref_str: str,
    db: Session
) -> VendasResponse:
    """
    Retorna vendas do LÍDER + vendas da EQUIPE (liderados).
    
    REGRA ESPECIAL PARA COORDENADORES/GERENTES:
    - Busca TODAS as vendas da FILIAL (não apenas dos IDs cadastrados)
    - Inclui: equipe ativa + desligados + colaboradores sem meta cadastrada
    
    Args:
        cod_usuario_lider: ID do colaborador líder
        nome_lider: Nome do líder direto
        mes_referencia: Data de referência do mês
        mes_ref_str: Mês no formato 'YYYY-MM-DD'
        db: Sessão do banco de dados
    """
    print(f"--- [VENDAS LIDERADOS] Iniciando busca RECURSIVA ---")
    print(f"    Líder: {nome_lider}")
    print(f"    ID Líder: {cod_usuario_lider}")
    print(f"    Mês: {mes_ref_str}")
    
    # Buscar info do líder para verificar se é coordenador/gerente
    meta_lider = db.query(MetaColaborador).filter(
        MetaColaborador.id_eyal == cod_usuario_lider,
        MetaColaborador.mes_ref == mes_ref_str
    ).first()
    
    if not meta_lider:
        print(f"⚠️ [VENDAS] Líder {cod_usuario_lider} não encontrado em metas_colaboradores")
        return VendasResponse(success=True, resumo=None, detalhes=[], message="Líder não encontrado")
    
    cargo_lower = (meta_lider.cargo or "").lower()
    eh_gerente = 'gerente' in cargo_lower
    eh_coordenador = 'coordenador' in cargo_lower
    eh_supervisor = 'supervisor' in cargo_lower or 'monitor' in cargo_lower
    
    # ========================================
    # GERENTES: TODA A FILIAL
    # ========================================
    if eh_gerente:
        print(f"--- [VENDAS] 🏢 GERENTE: Buscando TODAS vendas da filial '{meta_lider.unidade}' ---")
        
        vendas = db.query(BaseCampanhas).filter(
            and_(
                BaseCampanhas.filial == meta_lider.unidade,
                extract('year', BaseCampanhas.mes) == mes_referencia.year,
                extract('month', BaseCampanhas.mes) == mes_referencia.month
            )
        ).all()
        
        print(f"    ✅ Total de vendas da filial: {len(vendas)}")
        
        ids_unicos_vendedores = set([v.cod_usuario for v in vendas])
        print(f"    ℹ️ {len(ids_unicos_vendedores)} vendedores únicos")
        
        total_liderados = len(ids_unicos_vendedores)
    
    # ========================================
    # COORDENADORES/SUPERVISORES: APENAS HIERARQUIA
    # ========================================
    elif eh_coordenador or eh_supervisor:
        print(f"--- [VENDAS] 👥 {cargo_lower.upper()}: Apenas hierarquia cadastrada ---")
        
        # 1. Buscar liderados DIRETOS (nível 1)
        liderados_diretos = db.query(MetaColaborador).filter(
            MetaColaborador.lider_direto == nome_lider,
            MetaColaborador.mes_ref == mes_ref_str
        ).all()
        
        print(f"    Nível 1: Encontrados {len(liderados_diretos)} liderados diretos")
        
        # 2. Lista de IDs para buscar (líder + liderados de todos os níveis)
        ids_para_buscar = [cod_usuario_lider]  # Inclui o próprio líder
        nomes_supervisores = []  # Para buscar nível 2
        
        for liderado in liderados_diretos:
            if liderado.id_eyal:
                ids_para_buscar.append(liderado.id_eyal)
                print(f"    + '{liderado.id_eyal}' - {liderado.nome} ({liderado.cargo})")
                
                # Se for supervisor/monitor, guardar nome para buscar equipe dele
                cargo_liderado_lower = (liderado.cargo or "").lower()
                if any(c in cargo_liderado_lower for c in ["supervisor", "monitor", "orientador"]):
                    nomes_supervisores.append(liderado.nome)
        
        # 3. Buscar liderados dos supervisores (nível 2 - vendedores)
        if nomes_supervisores:
            print(f"    Nível 2: Buscando equipes de {len(nomes_supervisores)} supervisores")
            
            liderados_nivel2 = db.query(MetaColaborador).filter(
                MetaColaborador.lider_direto.in_(nomes_supervisores),
                MetaColaborador.mes_ref == mes_ref_str
            ).all()
            
            print(f"    Encontrados {len(liderados_nivel2)} vendedores nas equipes")
            
            for vendedor in liderados_nivel2:
                if vendedor.id_eyal and vendedor.id_eyal not in ids_para_buscar:
                    ids_para_buscar.append(vendedor.id_eyal)
                    print(f"    + '{vendedor.id_eyal}' - {vendedor.nome}")
        
        print(f"    Total de IDs (todos níveis): {len(ids_para_buscar)}")
        
        # Buscar vendas da hierarquia
        vendas = db.query(BaseCampanhas).filter(
            and_(
                BaseCampanhas.cod_usuario.in_(ids_para_buscar),
                extract('year', BaseCampanhas.mes) == mes_referencia.year,
                extract('month', BaseCampanhas.mes) == mes_referencia.month
            )
        ).all()
        
        print(f"    ✅ TOTAL: {len(vendas)} vendas da hierarquia")
        
        total_liderados = len(ids_para_buscar)
    
    # ========================================
    # ATENDENTES: VENDAS PRÓPRIAS
    # ========================================
    else:
        print(f"--- [VENDAS] 👤 ATENDENTE: Vendas próprias ---")
        
        vendas = db.query(BaseCampanhas).filter(
            and_(
                BaseCampanhas.cod_usuario == cod_usuario_lider,
                extract('year', BaseCampanhas.mes) == mes_referencia.year,
                extract('month', BaseCampanhas.mes) == mes_referencia.month
            )
        ).all()
        
        total_liderados = 1
    
    print(f"--- [VENDAS LIDERADOS] Total de vendas encontradas: {len(vendas)} ---")
    
    # Debug: Contar vendas por pessoa
    if vendas:
        from collections import Counter
        vendas_por_pessoa = Counter([v.cod_usuario for v in vendas])
        print(f"    Vendas por pessoa:")
        for cod_usuario, qtd in vendas_por_pessoa.most_common(10):
            print(f"      {cod_usuario}: {qtd} vendas")
    
    if not vendas:
        return VendasResponse(
            success=True,
            resumo=None,
            detalhes=[],
            message=f"Nenhuma venda encontrada para {nome_lider} e sua equipe"
        )
    
    # 4. Processar vendas (mesma lógica do endpoint original)
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
    
    # 🐛 DEBUG: Contadores de classificação
    debug_grupos_raw = []
    
    for venda in vendas:
        categoria = classificar_grupo(venda.grupo_exames or "", venda.abrev_exame or "")
        
        # 🐛 DEBUG: Guardar valores para análise
        if categoria == 'ODONTO' or 'ODONTO' in (venda.grupo_exames or "").upper():
            debug_grupos_raw.append(venda.grupo_exames)
        
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
    
    # 🐛 DEBUG: Mostrar classificação de ODONTO
    if debug_grupos_raw:
        print(f"    🔍 DEBUG ODONTO: {len(debug_grupos_raw)} vendas com 'ODONTO' no grupo_exames")
        print(f"    🔍 Contador classificou como ODONTO: {contadores['odonto']} vendas")
        from collections import Counter
        contagem_grupos = Counter(debug_grupos_raw)
        for grupo, qtd in contagem_grupos.most_common():
            print(f"   '{grupo}': {qtd} vendas")
    
    # 5. Montar resumo com informação de liderados
    # Definir tipo de busca para mensagem
    if eh_gerente:
        tipo_busca = "FILIAL"
        nome_display = f"{nome_lider} + FILIAL ({total_liderados} vendedores)"
    elif eh_coordenador or eh_supervisor:
        tipo_busca = f"{total_liderados} liderados (hierarquia + desligados)"
        nome_display = f"{nome_lider} + EQUIPE ({total_liderados} pessoas)"
    else:
        tipo_busca = "VENDAS PRÓPRIAS"
        nome_display = nome_lider
    
    resumo = ResumoVendas(
        cod_usuario=cod_usuario_lider,
        nome_usuario=nome_display,
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
    
    print(f"--- [VENDAS] Total de vendas ({tipo_busca}): {len(vendas)} | Valor total: R$ {valor_total:.2f} ---")
    
    return VendasResponse(
        success=True,
        resumo=resumo,
        detalhes=detalhes_list,
        message=f"Vendas incluem {nome_lider} + {tipo_busca}"
    )
