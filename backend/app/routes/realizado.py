from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.realizado_colaboradores import RealizadoColaborador
from app.models.metas_colaboradores import MetaColaborador
from app.schemas.realizado import RealizadoColaborador as RealizadoSchema
from sqlalchemy import func


from pydantic import BaseModel
from typing import List

router = APIRouter(
    prefix="/realizado",
    tags=["Realizado"]
)

@router.get("/colaborador/{identificador}", response_model=List[RealizadoSchema])
def get_realizado_colaborador(identificador: int, db: Session = Depends(get_db)):
    """
    Retorna os dados realizados de um colaborador com base no id_eyal.
    """
    # A consulta já está correta para buscar todos os registros com .all()
    realizados = db.query(RealizadoColaborador).filter(
        RealizadoColaborador.id_eyal == identificador
    ).all()
    if not realizados:
        raise HTTPException(status_code=404, detail="Dados de 'realizado' não encontrados para o colaborador.")

    return realizados

# Rota principal do realizado com regras de negócio
@router.get("/resumo/{identificador}")
def get_resumo_colaborador(identificador: int, db: Session = Depends(get_db)):
    """
    ROTA PRINCIPAL DO REALIZADO COM REGRAS DE NEGÓCIO
    
    Retorna um resumo com os totais realizados aplicando as regras de negócio:
    
    REGRAS DE NEGÓCIO REFINADAS:
    1. CARGOS ESPECIAIS: supervisor de atendimento, monitor, orientador -> próprio realizado + realizado dos liderados
    2. Líderes experientes -> próprio realizado + realizado de toda unidade
    3. Líderes gerais -> próprio realizado + realizado de toda unidade
    4. Senão -> apenas próprio realizado
    """
    return _aplicar_regras_negocio_realizado(identificador, db)

# Rota detalhada para o resumo com regras de liderança (mantida para compatibilidade)
@router.get("/colaborador/{identificador}/resumo")
def get_resumo_colaborador_detalhado(identificador: int, db: Session = Depends(get_db)):
    """
    ROTA DETALHADA - Retorna um resumo com os totais realizados de um colaborador,
    agrupados por tipo_grupo, e um total geral.
    
    REGRAS DE NEGÓCIO REFINADAS:
    1. Líderes experientes COM liderados -> incluir liderados
    2. Líderes da Central de Marcações (cargos específicos) -> incluir toda unidade  
    3. Líderes gerais -> incluir toda unidade
    4. Senão -> apenas próprio realizado
    """
    return _aplicar_regras_negocio_realizado(identificador, db)


def _aplicar_regras_negocio_realizado(identificador: int, db: Session):
    """
    FUNÇÃO CORE - Aplica as regras de negócio para cálculo do realizado
    
    REGRAS DE NEGÓCIO REFINADAS:
    1. CARGOS ESPECIAIS: supervisor de atendimento, monitor, orientador -> próprio realizado + realizado dos liderados
    2. Líderes experientes -> próprio realizado + realizado de toda unidade
    3. Líderes gerais -> próprio realizado + realizado de toda unidade
    4. Senão -> apenas próprio realizado
    """
    
    # Primeiro, verificar se o colaborador é um líder experiente
    meta_colaborador = db.query(MetaColaborador).filter(
        MetaColaborador.id_eyal == str(identificador)
    ).first()
    
    if not meta_colaborador:
        print(f"--- [REALIZADO] Colaborador {identificador} não encontrado nas metas ---")
        # Se não tem meta, busca apenas o realizado direto
        return _get_resumo_basico(identificador, db)
    
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
    
    # Verificar unidade - usar a unidade do realizado, não da meta
    unidade_realizado = None
    realizados_colaborador = db.query(RealizadoColaborador).filter(
        RealizadoColaborador.id_eyal == identificador
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
        return _get_resumo_com_liderados(identificador, meta_colaborador.nome, db)
    elif eh_lider_geral and eh_experiente:
        # Líderes experientes recebem próprio + unidade
        print(f"--- [REALIZADO] Líder experiente. Usando regra de unidade: {unidade} ---")
        return _get_resumo_por_unidade(identificador, unidade, db)
    elif eh_lider_geral:
        print(f"--- [REALIZADO] Líder geral. Usando regra de unidade: {unidade} ---")
        return _get_resumo_por_unidade(identificador, unidade, db)
    else:
        print(f"--- [REALIZADO] Colaborador normal. Usando regra básica ---")
        return _get_resumo_basico(identificador, db)


def _get_resumo_por_unidade(identificador: int, unidade: str, db: Session):
    """Retorna o realizado de todos os colaboradores da mesma unidade baseado na tabela realizado_colaborador"""
    
    print(f"--- [REALIZADO] Buscando todos da unidade: '{unidade}' ---")
    
    # Buscar todos os IDs que têm registros na mesma unidade na tabela realizado_colaborador
    colaboradores_unidade = db.query(RealizadoColaborador.id_eyal).filter(
        RealizadoColaborador.unidade == unidade
    ).distinct().all()
    
    # Extrair IDs únicos
    ids_unidade = [colab.id_eyal for colab in colaboradores_unidade if colab.id_eyal]
    
    print(f"--- [REALIZADO] Encontrados {len(ids_unidade)} colaboradores na unidade ---")
    print(f"--- [REALIZADO] IDs da unidade: {ids_unidade[:10]}{'...' if len(ids_unidade) > 10 else ''} ---")
    
    if not ids_unidade:
        # Fallback para apenas o colaborador atual
        return _get_resumo_basico(identificador, db)
    
    # Buscar realizado de todos da unidade
    resumo_por_grupo = db.query(
        RealizadoColaborador.tipo_grupo,
        func.sum(RealizadoColaborador.total_realizado).label("total")
    ).filter(
        RealizadoColaborador.id_eyal.in_(ids_unidade)
    ).group_by(
        RealizadoColaborador.tipo_grupo
    ).all()

    resumo_final = {item.tipo_grupo: item.total for item in resumo_por_grupo}
    total_geral = sum(resumo_final.values())
    resumo_final["TOTAL_GERAL"] = total_geral
    resumo_final["INCLUI_UNIDADE"] = True  # Flag para indicar que inclui toda unidade
    resumo_final["QTDE_COLABORADORES_UNIDADE"] = len(ids_unidade)
    resumo_final["UNIDADE"] = unidade

    if not resumo_final or total_geral == 0:
        # Fallback para apenas o colaborador atual
        return _get_resumo_basico(identificador, db)

    return resumo_final


def _get_resumo_basico(identificador: int, db: Session):
    """Retorna apenas o realizado do próprio colaborador"""
    resumo_por_grupo = db.query(
        RealizadoColaborador.tipo_grupo,
        func.sum(RealizadoColaborador.total_realizado).label("total")
    ).filter(
        RealizadoColaborador.id_eyal == identificador
    ).group_by(
        RealizadoColaborador.tipo_grupo
    ).all()

    resumo_final = {item.tipo_grupo: item.total for item in resumo_por_grupo}
    total_geral = sum(resumo_final.values())
    resumo_final["TOTAL_GERAL"] = total_geral

    if not resumo_final:
        raise HTTPException(status_code=404, detail="Dados não encontrados.")

    return resumo_final


def _get_resumo_com_liderados(identificador: int, nome_lider: str, db: Session):
    """Retorna o realizado do líder + realizado dos liderados"""
    
    # 1. Buscar todos os liderados diretos
    liderados = db.query(MetaColaborador).filter(
        MetaColaborador.lider_direto == nome_lider
    ).all()
    
    print(f"--- [REALIZADO] Encontrados {len(liderados)} liderados para {nome_lider} ---")
    
    # 2. Lista de IDs para buscar (líder + liderados)
    ids_para_buscar = [identificador]  # Inclui o próprio líder
    
    for liderado in liderados:
        if liderado.id_eyal and liderado.id_eyal.isdigit():
            ids_para_buscar.append(int(liderado.id_eyal))
            print(f"    Liderado: {liderado.nome} (ID: {liderado.id_eyal})")
    
    print(f"--- [REALIZADO] Buscando realizado para IDs: {ids_para_buscar} ---")
    
    # 3. Buscar realizado de todos (líder + liderados)
    resumo_por_grupo = db.query(
        RealizadoColaborador.tipo_grupo,
        func.sum(RealizadoColaborador.total_realizado).label("total")
    ).filter(
        RealizadoColaborador.id_eyal.in_(ids_para_buscar)
    ).group_by(
        RealizadoColaborador.tipo_grupo
    ).all()

    resumo_final = {item.tipo_grupo: item.total for item in resumo_por_grupo}
    total_geral = sum(resumo_final.values())
    resumo_final["TOTAL_GERAL"] = total_geral
    resumo_final["INCLUI_LIDERADOS"] = True  # Flag para indicar que inclui liderados
    resumo_final["QTDE_LIDERADOS"] = len(liderados)

    if not resumo_final or total_geral == 0:
        raise HTTPException(status_code=404, detail="Dados não encontrados.")

    return resumo_final


# Rota original mantida para compatibilidade
@router.get("/colaborador/{identificador}/resumo-original")
def get_resumo_colaborador_original(identificador: int, db: Session = Depends(get_db)):
    """
    Retorna um resumo com os totais realizados APENAS do colaborador,
    sem aplicar regras de liderança (rota original).
    """
    return _get_resumo_basico(identificador, db)

# 1. Crie um novo Schema para a resposta da nova rota.
#    Isso define como será o JSON de saída.
class RealizadoUnidadeSchema(BaseModel):
    unidade: str
    total_realizado: float

    class Config:
        from_attributes = True # Permite que o Pydantic leia dados de objetos SQLAlchemy

# 2. Adicione a nova rota ao seu router existente.
@router.get("/unidade", response_model=List[RealizadoUnidadeSchema])
def get_realizado_por_unidade(db: Session = Depends(get_db)):
    """
    Retorna a soma do total realizado para todos os colaboradores,
    agrupado por unidade.
    """
    # A query com SQLAlchemy para agrupar por 'unidade' e somar 'total_realizado'
    # Removemos o filtro por 'id_eyal' para incluir todos os colaboradores.
    realizado_agrupado = db.query(
        RealizadoColaborador.unidade,
        func.sum(RealizadoColaborador.total_realizado).label("total_realizado")
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
def get_realizado_por_unidade_especifica(nome_unidade: str, db: Session = Depends(get_db)):
    """
    Retorna a SOMA do total realizado para todos os colaboradores
    de UMA unidade específica.
    """
    # 1. A query agora soma 'total_realizado' e filtra pela unidade.
    #    O .scalar() pega o resultado único da soma.
    soma_total = db.query(
        func.sum(RealizadoColaborador.total_realizado)
    ).filter(
        RealizadoColaborador.unidade == nome_unidade
    ).scalar()

    # 2. Se a unidade não existir ou não tiver registros, a soma será None.
    if soma_total is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Nenhum dado de 'realizado' encontrado para a unidade: {nome_unidade}"
        )

    # 3. Retorna um dicionário que corresponde ao schema 'RealizadoUnidadeSchema'.
    return {"unidade": nome_unidade, "total_realizado": soma_total}


# === NOVA ROTA: RELATÓRIO RESUMO DAS METAS ===
@router.get("/relatorio/resumo-metas")
def get_relatorio_resumo_metas(db: Session = Depends(get_db)):
    """
    RELATÓRIO RESUMO DAS METAS - Retorna estrutura completa como no Excel
    
    Retorna:
    - Resumo das Metas por Unidade (seção principal)
    - Resumo Gerentes (Coordenadoras das Unidades) 
    - Resumo Coordenadores (Coordenadoras das Unidades)
    - Resumo Líderes CM (Líderes da Central de Mercações)
    
    Cada item contém: Meta, Realizado (Consultas/Exames/Odonto), %, Total Realizado, % Atingido, etc.
    """
    try:
        print("=== DEBUG: Iniciando relatório resumo metas ===")
        
        # Verificar dados básicos primeiro
        total_metas = db.query(MetaColaborador).count()
        total_realizados = db.query(RealizadoColaborador).count()
        print(f"DEBUG: Total metas: {total_metas}, Total realizados: {total_realizados}")
        
        # Estrutura do relatório
        relatorio = {
            "titulo": "Resumo das Metas SETEMBRO/2025",
            "data_geracao": "2025-09-30",
            "dias_trabalhados": 22.5,
            "debug_info": {
                "total_metas": total_metas,
                "total_realizados": total_realizados
            },
            "secoes": {
                "unidades": _get_resumo_unidades(db),
                "gerentes": _get_resumo_gerentes(db), 
                "coordenadores": _get_resumo_coordenadores(db),
                "lideres_cm": _get_resumo_lideres_cm(db)
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
def _get_resumo_unidades(db: Session):
    """Retorna resumo das metas por unidade (seção principal)"""
    try:
        print("=== DEBUG: Iniciando _get_resumo_unidades ===")
        
        # Buscar todas as unidades com metas e realizados
        unidades = db.query(MetaColaborador.unidade).distinct().all()
        print(f"DEBUG: Encontradas {len(unidades)} unidades distintas")
        
        resumo_unidades = []
        
        for unidade_row in unidades:
            unidade = unidade_row.unidade
            print(f"DEBUG: Processando unidade: '{unidade}'")
            
            if not unidade:
                print("DEBUG: Unidade vazia, pulando...")
                continue
                
            # Buscar meta total da unidade
            meta_total = db.query(func.sum(MetaColaborador.meta_final)).filter(
                MetaColaborador.unidade == unidade
            ).scalar() or 0
            print(f"DEBUG: Meta total da unidade '{unidade}': {meta_total}")
            
            # Buscar realizado por tipo para esta unidade
            realizados = db.query(
                RealizadoColaborador.tipo_grupo,
                func.sum(RealizadoColaborador.total_realizado).label("total")
            ).filter(
                RealizadoColaborador.unidade == unidade
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


def _get_resumo_gerentes(db: Session):
    """Retorna resumo dos gerentes (coordenadoras das unidades)"""
    try:
        print("=== DEBUG: Iniciando _get_resumo_gerentes ===")
        
        # Buscar colaboradores com cargo de gerente
        gerentes = db.query(MetaColaborador).filter(
            MetaColaborador.cargo.ilike('%gerente%')
        ).all()
        
        print(f"DEBUG: Encontrados {len(gerentes)} gerentes")
        
        resumo_gerentes = []
        
        for gerente in gerentes:
            print(f"DEBUG: Processando gerente: {gerente.nome} - {gerente.cargo}")
            
            # Aplicar regras de negócio para o gerente
            resultado = _aplicar_regras_negocio_realizado(int(gerente.id_eyal), db)
            
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


def _get_resumo_coordenadores(db: Session):
    """Retorna resumo dos coordenadores"""
    try:
        # Buscar colaboradores com cargo de coordenador
        coordenadores = db.query(MetaColaborador).filter(
            MetaColaborador.cargo.ilike('%coordenador%')
        ).all()
        
        resumo_coordenadores = []
        
        for coordenador in coordenadores:
            # Aplicar regras de negócio para o coordenador
            resultado = _aplicar_regras_negocio_realizado(int(coordenador.id_eyal), db)
            
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


def _get_resumo_lideres_cm(db: Session):
    """Retorna resumo dos líderes da Central de Mercações"""
    try:
        print("=== DEBUG: Iniciando _get_resumo_lideres_cm ===")
        
        # Buscar líderes da Central de Mercações
        print("DEBUG: Buscando por cargos específicos...")
        lideres_cm = db.query(MetaColaborador).filter(
            MetaColaborador.unidade.ilike('%central%marcação%')
        ).filter(
            MetaColaborador.cargo.ilike('%supervisor%') |
            MetaColaborador.cargo.ilike('%monitor%') |
            MetaColaborador.cargo.ilike('%orientador%')
        ).all()
        
        print(f"DEBUG: Encontrados {len(lideres_cm)} líderes CM")
        if len(lideres_cm) == 0:
            # Tentar busca mais ampla por cargos
            print("DEBUG: Tentando busca mais ampla por cargos...")
            todos_cargos_central = db.query(MetaColaborador.cargo).filter(
                MetaColaborador.unidade.ilike('%central%')
            ).distinct().all()
            
            print("DEBUG: Cargos encontrados na Central:")
            for cargo_row in todos_cargos_central[:10]:
                print(f"  - {cargo_row.cargo}")
                
            # Buscar com any supervisor, monitor, orientador
            lideres_cm = db.query(MetaColaborador).filter(
                MetaColaborador.unidade.ilike('%central%')
            ).filter(
                MetaColaborador.cargo.ilike('%supervisor%') |
                MetaColaborador.cargo.ilike('%monitor%') |
                MetaColaborador.cargo.ilike('%orientador%')
            ).all()
            
            print(f"DEBUG: Com busca ampla encontrados {len(lideres_cm)} líderes")
        
        resumo_lideres = []
        
        for lider in lideres_cm:
            print(f"DEBUG: Processando líder CM: {lider.nome} - {lider.cargo}")
            
            # Aplicar regras de negócio para o líder
            resultado = _aplicar_regras_negocio_realizado(int(lider.id_eyal), db)
            
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

