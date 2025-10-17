"""
Rotas para o módulo de Comissões
Calcula comissões baseadas nas vendas e valores configurados por procedimento

REGRA DE NEGÓCIO:
- COORDENADORES/GERENTES: TODAS as vendas da FILIAL
  (inclui: equipe ativa + desligados + sem meta cadastrada)
- SUPERVISORES: Vendas da equipe ativa (liderados diretos)
- ATENDENTES: Vendas próprias
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import extract, or_
from datetime import datetime, date
from typing import Optional
from collections import defaultdict

from app.database import get_db
from app.models.metas_colaboradores import MetaColaborador
from app.models.vendas import BaseCampanhas
from app.models.dados_camp_proc_historico import DadosCampProcHistorico
from app.schemas.comissao import (
    ComissaoColaboradorResponse,
    ComissaoPorCategoria,
    VendaComissaoItem,
    ComissaoResumo,
    ProcedimentoComissaoResponse,
    ProcedimentoComissaoCreate,
    ProcedimentoComissaoUpdate
)

router = APIRouter(
    prefix="/comissao",
    tags=["Comissões"]
)


@router.get(
    "/resumo/{id_eyal}",
    response_model=ComissaoResumo,
    summary="Resumo simplificado de comissão"
)
async def get_comissao_resumo(
    id_eyal: str,
    mes_ref: Optional[str] = Query(None, description="Mês de referência (YYYY-MM)"),
    db: Session = Depends(get_db)
):
    """
    Retorna resumo simplificado da comissão (para cards no dashboard)
    """
    # Redirecionar para cálculo completo e extrair resumo
    comissao_completa = await calcular_comissao_colaborador(
        id_eyal=id_eyal,
        mes_ref=mes_ref,
        incluir_detalhes=False,
        db=db
    )
    
    return ComissaoResumo(
        total_comissao=comissao_completa.total_comissao,
        projecao_meta=comissao_completa.projecao_meta_realizada,
        campanhas=comissao_completa.campanhas,
        quantidade_vendas=comissao_completa.total_procedimentos
    )


@router.get(
    "/colaborador/{id_eyal}",
    response_model=ComissaoColaboradorResponse,
    summary="Calcular comissão completa de um colaborador"
)
async def calcular_comissao_colaborador(
    id_eyal: str,
    mes_ref: Optional[str] = Query(None, description="Mês de referência (YYYY-MM ou YYYY-MM-DD)"),
    incluir_detalhes: bool = Query(True, description="Incluir detalhamento das vendas"),
    db: Session = Depends(get_db)
):
    """
    Calcula a comissão de um colaborador baseado em:
    1. Hierarquia (líder recebe sobre equipe/filial)
    2. Valores configurados por procedimento
    3. Cargo do colaborador
    
    REGRA PARA COORDENADORES/GERENTES:
    - Recebe sobre TODAS as vendas da FILIAL
    - Inclui: colaboradores ativos + desligados + sem meta cadastrada
    - Exemplo: Bruna (coordenadora) recebe sobre TODAS vendas de 'CENTRAL DE MARCACÕES'
    """
    
    try:
        print("\n" + "="*60)
        print(f"[COMISSÃO] Calculando comissão para {id_eyal}")
        print("="*60)
        
        # 1. Determinar mês de referência
        if mes_ref:
            try:
                if len(mes_ref) == 7:  # YYYY-MM
                    mes_referencia = datetime.strptime(mes_ref, "%Y-%m").date()
                elif len(mes_ref) == 10:  # YYYY-MM-DD
                    mes_referencia = datetime.strptime(mes_ref, "%Y-%m-%d").date()
                else:
                    raise ValueError("Formato inválido")
                mes_ref_date = mes_referencia.replace(day=1)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Formato de data inválido. Use YYYY-MM ou YYYY-MM-DD"
                )
        else:
            hoje = datetime.now().date()
            mes_ref_date = hoje.replace(day=1)
            mes_referencia = mes_ref_date
        
        print(f"[COMISSÃO] Mês: {mes_ref_date}")
        
        # 2. Buscar dados do colaborador
        colaborador = db.query(MetaColaborador).filter(
            MetaColaborador.id_eyal == id_eyal,
            MetaColaborador.mes_ref == mes_ref_date
        ).first()
        
        if not colaborador:
            raise HTTPException(
                status_code=404,
                detail=f"Colaborador {id_eyal} não encontrado para o mês {mes_ref_date}"
            )
        
        cargo = colaborador.cargo or "ATENDENTE"
        nome_lider = colaborador.nome
        print(f"[COMISSÃO] Cargo: {cargo}")
        print(f"[COMISSÃO] Mês: {mes_ref_date}")
        
        # 3. Determinar IDs para busca de vendas (hierarquia)
        ids_para_buscar = [id_eyal]  # Sempre inclui o próprio colaborador
        cargo_lower = cargo.lower()
        
        # Se é líder (coordenador, gerente, supervisor), buscar equipe
        if any(x in cargo_lower for x in ['coordenador', 'gerente', 'supervisor', 'monitor']):
            print(f"[COMISSÃO] Colaborador é LÍDER - buscando vendas da equipe")
            
            # Nível 1: Liderados diretos
            liderados_diretos = db.query(MetaColaborador).filter(
                MetaColaborador.lider_direto == nome_lider,
                MetaColaborador.mes_ref == mes_ref_date
            ).all()
            
            print(f"[COMISSÃO] Nível 1: Encontrados {len(liderados_diretos)} liderados diretos")
            
            nomes_supervisores = []
            for liderado in liderados_diretos:
                if liderado.id_eyal:
                    ids_para_buscar.append(liderado.id_eyal)
                    
                # Se o liderado é supervisor, guardar nome para busca nível 2
                liderado_cargo_lower = (liderado.cargo or "").lower()
                if 'supervisor' in liderado_cargo_lower or 'monitor' in liderado_cargo_lower:
                    nomes_supervisores.append(liderado.nome)
            
            # Nível 2: Equipes dos supervisores (apenas para coordenadores/gerentes)
            if nomes_supervisores and ('coordenador' in cargo_lower or 'gerente' in cargo_lower):
                print(f"[COMISSÃO] Nível 2: Buscando equipes de {len(nomes_supervisores)} supervisores")
                
                liderados_nivel2 = db.query(MetaColaborador).filter(
                    MetaColaborador.lider_direto.in_(nomes_supervisores),
                    MetaColaborador.mes_ref == mes_ref_date
                ).all()
                
                print(f"[COMISSÃO] Nível 2: {len(liderados_nivel2)} vendedores encontrados")
                
                for vendedor in liderados_nivel2:
                    if vendedor.id_eyal:
                        ids_para_buscar.append(vendedor.id_eyal)
            
            # ADM: Funcionários sem equipe na mesma unidade (apenas coordenadores/gerentes)
            if 'coordenador' in cargo_lower or 'gerente' in cargo_lower:
                unidade_coord = colaborador.unidade
                print(f"[COMISSÃO] ADM: Buscando funcionários sem equipe na unidade '{unidade_coord}'")
                
                funcionarios_adm = db.query(MetaColaborador).filter(
                    MetaColaborador.mes_ref == mes_ref_date,
                    MetaColaborador.unidade == unidade_coord,
                    or_(
                        MetaColaborador.equipe.is_(None),
                        MetaColaborador.equipe == ''
                    ),
                    MetaColaborador.nome != nome_lider
                ).all()
                
                print(f"[COMISSÃO] ADM: Funcionários sem equipe encontrados: {len(funcionarios_adm)}")
                
                for func_adm in funcionarios_adm:
                    if func_adm.id_eyal and func_adm.id_eyal not in ids_para_buscar:
                        ids_para_buscar.append(func_adm.id_eyal)
                        print(f"[COMISSÃO] ADM: ✅ {func_adm.nome} (ID: {func_adm.id_eyal})")
        
        print(f"[COMISSÃO] Total de IDs para buscar vendas: {len(ids_para_buscar)}")
        
        # 4. Buscar vendas
        cargo_lower = (cargo or "").lower()
        eh_gerente = 'gerente' in cargo_lower
        eh_coordenador = 'coordenador' in cargo_lower
        eh_supervisor = 'supervisor' in cargo_lower or 'monitor' in cargo_lower
        
        # ========================================
        # GERENTES: TODA A FILIAL
        # ========================================
        if eh_gerente:
            print(f"[COMISSÃO] 🏢 GERENTE: Buscando TODAS vendas da filial '{colaborador.unidade}'")
            
            vendas = db.query(BaseCampanhas).filter(
                BaseCampanhas.filial == colaborador.unidade,
                extract('year', BaseCampanhas.mes) == mes_referencia.year,
                extract('month', BaseCampanhas.mes) == mes_referencia.month
            ).all()
            
            ids_unicos = set([v.cod_usuario for v in vendas])
            print(f"[COMISSÃO]    ✅ Total vendas: {len(vendas)} | Vendedores: {len(ids_unicos)}")
        
        # ========================================
        # COORDENADORES/SUPERVISORES: APENAS HIERARQUIA
        # ========================================
        elif eh_coordenador or eh_supervisor:
            print(f"[COMISSÃO] 👥 {cargo_lower.upper()}: Apenas hierarquia cadastrada")
            
            # Buscar vendas da hierarquia
            vendas = db.query(BaseCampanhas).filter(
                BaseCampanhas.cod_usuario.in_(ids_para_buscar),
                extract('year', BaseCampanhas.mes) == mes_referencia.year,
                extract('month', BaseCampanhas.mes) == mes_referencia.month
            ).all()
            
            print(f"[COMISSÃO]    ✅ TOTAL: {len(vendas)} vendas da hierarquia")
        
        # ========================================
        # ATENDENTES: VENDAS PRÓPRIAS
        # ========================================
        else:
            print(f"[COMISSÃO] 👤 ATENDENTE: Vendas próprias")
            
            vendas = db.query(BaseCampanhas).filter(
                BaseCampanhas.cod_usuario.in_(ids_para_buscar),
                extract('year', BaseCampanhas.mes) == mes_referencia.year,
                extract('month', BaseCampanhas.mes) == mes_referencia.month
            ).all()
            
            print(f"[COMISSÃO]    ✅ Total vendas: {len(vendas)}")
        
        print(f"[COMISSÃO] Total de vendas encontradas: {len(vendas)}")
        
        if not vendas:
            return ComissaoColaboradorResponse(
                colaborador={
                    "id_eyal": id_eyal,
                    "nome": colaborador.nome,
                    "cargo": cargo,
                    "unidade": colaborador.unidade
                },
                mes_ref=mes_ref_date.strftime("%Y-%m-%d"),
                total_comissao=0.0,
                total_vendas=0.0,
                total_procedimentos=0,
                por_categoria=[],
                projecao_meta_realizada=0.0,
                campanhas=0.0,
                dias_trabalhados=colaborador.dias_trabalhados,
                meta_mes=float(colaborador.meta_final or 0)
            )
        
        # 5. Buscar valores de comissão para este mês
        valores_comissao = db.query(DadosCampProcHistorico).filter(
            DadosCampProcHistorico.mes_ref == mes_ref_date
        ).all()
        
        tabela_comissoes = {str(vc.cod_exame): vc for vc in valores_comissao}
        print(f"[COMISSÃO] Valores de comissão cadastrados: {len(tabela_comissoes)} procedimentos")
        
        # 6. Calcular comissões por venda
        comissao_total = 0.0
        valor_vendas_total = 0.0
        comissoes_por_categoria = defaultdict(lambda: {
            "quantidade": 0,
            "valor_vendas": 0.0,
            "valor_comissao": 0.0,
            "vendas": []
        })
        
        for venda in vendas:
            cod_exame_str = str(venda.cod_exame) if venda.cod_exame else None
            valor_venda = float(venda.valor_original_proc or 0)
            grupo = venda.grupo_exames or "OUTROS"
            
            if cod_exame_str and cod_exame_str in tabela_comissoes:
                proc_comissao = tabela_comissoes[cod_exame_str]
                valor_comissao = proc_comissao.get_comissao_por_cargo(cargo)
                
                comissao_total += valor_comissao
                valor_vendas_total += valor_venda
                
                comissoes_por_categoria[grupo]["quantidade"] += 1
                comissoes_por_categoria[grupo]["valor_vendas"] += valor_venda
                comissoes_por_categoria[grupo]["valor_comissao"] += valor_comissao
                
                if incluir_detalhes:
                    venda_item = VendaComissaoItem(
                        cod_exame=int(venda.cod_exame),
                        descricao=proc_comissao.descricao or venda.nome_exame_ajustado or "Sem descrição",
                        grupo=grupo,
                        valor_procedimento=valor_venda,
                        valor_comissao=valor_comissao,
                        data_agenda=venda.data_agenda.date() if venda.data_agenda else None,
                        paciente=venda.cod_paciente
                    )
                    comissoes_por_categoria[grupo]["vendas"].append(venda_item)
        
        # 7. Montar resposta
        categorias_response = []
        for categoria, dados in comissoes_por_categoria.items():
            categorias_response.append(
                ComissaoPorCategoria(
                    categoria=categoria,
                    quantidade_vendas=dados["quantidade"],
                    valor_total_vendas=dados["valor_vendas"],
                    valor_total_comissao=dados["valor_comissao"],
                    vendas=dados["vendas"] if incluir_detalhes else []
                )
            )
        
        print("\n" + "="*60)
        print(f"[COMISSÃO] RESUMO:")
        print(f"  - Total de procedimentos: {len(vendas)}")
        print(f"  - Valor total em vendas: R$ {valor_vendas_total:,.2f}")
        print(f"  - Comissão total: R$ {comissao_total:,.2f}")
        print(f"  - Categorias: {len(categorias_response)}")
        print("="*60 + "\n")
        
        return ComissaoColaboradorResponse(
            colaborador={
                "id_eyal": id_eyal,
                "nome": colaborador.nome,
                "cargo": cargo,
                "unidade": colaborador.unidade
            },
            mes_ref=mes_ref_date.strftime("%Y-%m-%d"),
            total_comissao=comissao_total,
            total_vendas=valor_vendas_total,
            total_procedimentos=len(vendas),
            por_categoria=categorias_response,
            projecao_meta_realizada=comissao_total,  # Por enquanto, mesma coisa
            campanhas=0.0,  # TODO: Implementar lógica de campanhas
            dias_trabalhados=colaborador.dias_trabalhados,
            meta_mes=float(colaborador.meta_final or 0)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ [COMISSÃO] ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erro ao calcular comissão: {str(e)}")


# ===============================================================================
# CRUD DE PROCEDIMENTOS DE COMISSÃO
# ===============================================================================

@router.get(
    "/procedimentos",
    response_model=list[ProcedimentoComissaoResponse],
    summary="Listar procedimentos com valores de comissão"
)
async def listar_procedimentos_comissao(
    mes_ref: Optional[str] = Query(None, description="Mês de referência (YYYY-MM)"),
    grupo: Optional[str] = Query(None, description="Filtrar por grupo (ODONTO, CHECK UP, etc)"),
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """Lista procedimentos com valores de comissão configurados"""
    
    if mes_ref:
        try:
            mes_ref_date = datetime.strptime(mes_ref, "%Y-%m").date().replace(day=1)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM")
    else:
        mes_ref_date = datetime.now().date().replace(day=1)
    
    query = db.query(DadosCampProcHistorico).filter(
        DadosCampProcHistorico.mes_ref == mes_ref_date
    )
    
    if grupo:
        query = query.filter(DadosCampProcHistorico.grupo == grupo)
    
    procedimentos = query.offset(offset).limit(limit).all()
    
    return [
        ProcedimentoComissaoResponse(
            mes_ref=p.mes_ref.date() if isinstance(p.mes_ref, datetime) else p.mes_ref,
            cod_exame=p.cod_exame,
            descricao=p.descricao,
            valor=p.valor,
            abrev=p.abrev,
            grupo=p.grupo,
            operadores=p.operadores,
            gerente=p.gerente,
            coord=p.coord,
            super_=p.super
        )
        for p in procedimentos
    ]


@router.get(
    "/procedimentos/{cod_exame}",
    response_model=ProcedimentoComissaoResponse,
    summary="Buscar procedimento específico"
)
async def get_procedimento_comissao(
    cod_exame: int,
    mes_ref: Optional[str] = Query(None, description="Mês de referência (YYYY-MM)"),
    db: Session = Depends(get_db)
):
    """Busca um procedimento específico com seus valores de comissão"""
    
    if mes_ref:
        try:
            mes_ref_date = datetime.strptime(mes_ref, "%Y-%m").date().replace(day=1)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM")
    else:
        mes_ref_date = datetime.now().date().replace(day=1)
    
    procedimento = db.query(DadosCampProcHistorico).filter(
        DadosCampProcHistorico.mes_ref == mes_ref_date,
        DadosCampProcHistorico.cod_exame == cod_exame
    ).first()
    
    if not procedimento:
        raise HTTPException(
            status_code=404,
            detail=f"Procedimento {cod_exame} não encontrado para {mes_ref_date}"
        )
    
    return ProcedimentoComissaoResponse(
        mes_ref=procedimento.mes_ref.date() if isinstance(procedimento.mes_ref, datetime) else procedimento.mes_ref,
        cod_exame=procedimento.cod_exame,
        descricao=procedimento.descricao,
        valor=procedimento.valor,
        abrev=procedimento.abrev,
        grupo=procedimento.grupo,
        operadores=procedimento.operadores,
        gerente=procedimento.gerente,
        coord=procedimento.coord,
        super_=procedimento.super
    )


@router.post(
    "/procedimentos",
    response_model=ProcedimentoComissaoResponse,
    summary="Criar novo procedimento com valores de comissão"
)
async def criar_procedimento_comissao(
    procedimento: ProcedimentoComissaoCreate,
    db: Session = Depends(get_db)
):
    """Cria um novo procedimento com valores de comissão"""
    
    # Verificar se já existe
    existe = db.query(DadosCampProcHistorico).filter(
        DadosCampProcHistorico.mes_ref == procedimento.mes_ref,
        DadosCampProcHistorico.cod_exame == procedimento.cod_exame
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=409,
            detail=f"Procedimento {procedimento.cod_exame} já existe para {procedimento.mes_ref}"
        )
    
    novo_proc = DadosCampProcHistorico(
        mes_ref=procedimento.mes_ref,
        cod_exame=procedimento.cod_exame,
        descricao=procedimento.descricao,
        valor=procedimento.valor,
        abrev=procedimento.abrev,
        grupo=procedimento.grupo,
        operadores=procedimento.operadores,
        gerente=procedimento.gerente,
        coord=procedimento.coord,
        super=procedimento.super_
    )
    
    db.add(novo_proc)
    db.commit()
    db.refresh(novo_proc)
    
    return ProcedimentoComissaoResponse(
        mes_ref=novo_proc.mes_ref.date() if isinstance(novo_proc.mes_ref, datetime) else novo_proc.mes_ref,
        cod_exame=novo_proc.cod_exame,
        descricao=novo_proc.descricao,
        valor=novo_proc.valor,
        abrev=novo_proc.abrev,
        grupo=novo_proc.grupo,
        operadores=novo_proc.operadores,
        gerente=novo_proc.gerente,
        coord=novo_proc.coord,
        super_=novo_proc.super
    )


@router.put(
    "/procedimentos/{cod_exame}",
    response_model=ProcedimentoComissaoResponse,
    summary="Atualizar procedimento"
)
async def atualizar_procedimento_comissao(
    cod_exame: int,
    procedimento_update: ProcedimentoComissaoUpdate,
    mes_ref: str = Query(..., description="Mês de referência (YYYY-MM)"),
    db: Session = Depends(get_db)
):
    """Atualiza valores de comissão de um procedimento"""
    
    try:
        mes_ref_date = datetime.strptime(mes_ref, "%Y-%m").date().replace(day=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM")
    
    procedimento = db.query(DadosCampProcHistorico).filter(
        DadosCampProcHistorico.mes_ref == mes_ref_date,
        DadosCampProcHistorico.cod_exame == cod_exame
    ).first()
    
    if not procedimento:
        raise HTTPException(
            status_code=404,
            detail=f"Procedimento {cod_exame} não encontrado para {mes_ref_date}"
        )
    
    # Atualizar campos fornecidos
    update_data = procedimento_update.model_dump(exclude_unset=True)
    for campo, valor in update_data.items():
        if campo == 'super_':
            setattr(procedimento, 'super', valor)
        else:
            setattr(procedimento, campo, valor)
    
    db.commit()
    db.refresh(procedimento)
    
    return ProcedimentoComissaoResponse(
        mes_ref=procedimento.mes_ref.date() if isinstance(procedimento.mes_ref, datetime) else procedimento.mes_ref,
        cod_exame=procedimento.cod_exame,
        descricao=procedimento.descricao,
        valor=procedimento.valor,
        abrev=procedimento.abrev,
        grupo=procedimento.grupo,
        operadores=procedimento.operadores,
        gerente=procedimento.gerente,
        coord=procedimento.coord,
        super_=procedimento.super
    )


@router.delete(
    "/procedimentos/{cod_exame}",
    summary="Deletar procedimento"
)
async def deletar_procedimento_comissao(
    cod_exame: int,
    mes_ref: str = Query(..., description="Mês de referência (YYYY-MM)"),
    db: Session = Depends(get_db)
):
    """Remove um procedimento com seus valores de comissão"""
    
    try:
        mes_ref_date = datetime.strptime(mes_ref, "%Y-%m").date().replace(day=1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de data inválido. Use YYYY-MM")
    
    procedimento = db.query(DadosCampProcHistorico).filter(
        DadosCampProcHistorico.mes_ref == mes_ref_date,
        DadosCampProcHistorico.cod_exame == cod_exame
    ).first()
    
    if not procedimento:
        raise HTTPException(
            status_code=404,
            detail=f"Procedimento {cod_exame} não encontrado para {mes_ref_date}"
        )
    
    db.delete(procedimento)
    db.commit()
    
    return {"message": f"Procedimento {cod_exame} deletado com sucesso"}
