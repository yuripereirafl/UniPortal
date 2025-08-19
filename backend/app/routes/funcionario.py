from ..models.funcionario_cargo import FuncionarioCargo
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date
from ..models.funcionario import Funcionario as FuncionarioModel
from ..models.setor import Setor
from ..models.sistema import Sistema as SistemaModel
from ..models.grupo_email import GrupoEmail
from ..models.cargo import Cargo
from ..models.grupo_pasta import GrupoPasta
from ..schemas.funcionario import FuncionarioCreate, Funcionario as FuncionarioSchema, FuncionarioUpdate
from ..schemas.sistema import Sistema as SistemaSchema
from ..schemas.setor import SetorOut
from ..schemas.grupo_email import GrupoEmailOut
from ..schemas.grupo_pasta import GrupoPastaOut
from ..database import engine
from app.models.meta import Meta
from app.models.funcionario_meta import FuncionarioMeta

def converter_string_para_date(data_str):
    """Converte string de data para objeto date"""
    if not data_str or data_str.strip() == '':
        return None
    try:
        return datetime.strptime(data_str, '%Y-%m-%d').date()
    except ValueError:
        try:
            return datetime.strptime(data_str, '%d/%m/%Y').date()
        except ValueError:
            return None

router = APIRouter()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@router.post('/funcionarios/', response_model=FuncionarioSchema)
def adicionar_funcionario(funcionario: FuncionarioCreate):
    db = SessionLocal()
    novo_funcionario = FuncionarioModel(
        nome=funcionario.nome,
        sobrenome=funcionario.sobrenome,
        celular=funcionario.celular,
        email=funcionario.email,
        cpf=funcionario.cpf,
        data_afastamento=converter_string_para_date(funcionario.data_afastamento),
        tipo_contrato=funcionario.tipo_contrato,
        data_retorno=converter_string_para_date(funcionario.data_retorno),
        data_inativado=funcionario.data_inativado if funcionario.data_inativado not in ('', None) else None
    )
    db.add(novo_funcionario)
    db.commit()
    db.refresh(novo_funcionario)
    # Vínculo de cargo via FuncionarioCargo
    if funcionario.cargo_id:
        cargo_obj = db.query(Cargo).filter(Cargo.id == funcionario.cargo_id).first()
        if cargo_obj:
            novo_vinculo = FuncionarioCargo(
                funcionario_id=novo_funcionario.id,
                cargo_id=cargo_obj.id,
                dt_inicio=datetime.now().date(),
                cargo_nome=cargo_obj.nome,
                cargo_nivel=getattr(cargo_obj, 'nivel', None),
                cargo_funcao=getattr(cargo_obj, 'funcao', None),
                cargo_equipe=getattr(cargo_obj, 'equipe', None)
            )
            db.add(novo_vinculo)
            db.commit()
    # Vincula setores
    if funcionario.setores_ids:
        setores = db.query(Setor).filter(Setor.id.in_(funcionario.setores_ids)).all()
        novo_funcionario.setores = setores
    else:
        novo_funcionario.setores = []
    # Vincula sistemas
    if funcionario.sistemas_ids:
        sistemas = db.query(SistemaModel).filter(SistemaModel.id.in_(funcionario.sistemas_ids)).all()
        novo_funcionario.sistemas = sistemas
    else:
        novo_funcionario.sistemas = []
    # Vincula grupos de e-mail
    if funcionario.grupos_email_ids:
        grupos = db.query(GrupoEmail).filter(GrupoEmail.id.in_(funcionario.grupos_email_ids)).all()
        novo_funcionario.grupos_email = grupos
    else:
        novo_funcionario.grupos_email = []
    # Vincula grupos de pasta
    if hasattr(funcionario, 'grupos_pasta_ids') and funcionario.grupos_pasta_ids:
        grupos_pasta = db.query(GrupoPasta).filter(GrupoPasta.id.in_(funcionario.grupos_pasta_ids)).all()
        novo_funcionario.grupos_pasta = grupos_pasta
    else:
        novo_funcionario.grupos_pasta = []
    db.commit()
    db.refresh(novo_funcionario)
    # Remove _sa_instance_state do dict antes de passar para o Pydantic
    funcionario_dict = dict(novo_funcionario.__dict__)
    funcionario_dict.pop('_sa_instance_state', None)
    funcionario_schema = FuncionarioSchema.model_validate({
    **funcionario_dict,
        'setores': [SetorOut.from_orm(setor) for setor in novo_funcionario.setores],
        'sistemas': [SistemaSchema.from_orm(sistema) for sistema in novo_funcionario.sistemas],
        'grupos_email': [GrupoEmailOut.from_orm(grupo) for grupo in novo_funcionario.grupos_email],
        'grupos_pasta': [GrupoPastaOut.from_orm(grupo) for grupo in novo_funcionario.grupos_pasta],
        'cargo': None if not hasattr(novo_funcionario, 'cargos_vinculos') or not novo_funcionario.cargos_vinculos else (
            novo_funcionario.cargos_vinculos[0].cargo.nome if novo_funcionario.cargos_vinculos[0].cargo else None
        ),
        'data_admissao': str(novo_funcionario.data_admissao) if novo_funcionario.data_admissao not in (None, '') else '',
        'data_inativado': str(novo_funcionario.data_inativado) if novo_funcionario.data_inativado is not None else '',
        'cpf': novo_funcionario.cpf,
        'data_afastamento': str(novo_funcionario.data_afastamento) if novo_funcionario.data_afastamento else None,
        'tipo_contrato': novo_funcionario.tipo_contrato,
        'data_retorno': str(novo_funcionario.data_retorno) if novo_funcionario.data_retorno else None
    })
    db.close()
    return funcionario_schema

@router.get('/funcionarios/{id}/sistemas', response_model=list[SistemaSchema])
def get_funcionario_sistemas(id: int):
    db = SessionLocal()
    funcionario = db.query(FuncionarioModel).filter(FuncionarioModel.id == id).first()
    if funcionario:
        sistemas = funcionario.sistemas
    else:
        sistemas = []
    db.close()
    return sistemas

@router.put('/funcionarios/{id}', response_model=FuncionarioSchema)
def atualizar_funcionario(id: int, funcionario: FuncionarioUpdate):
    db = SessionLocal()
    db_funcionario = db.query(FuncionarioModel).filter(FuncionarioModel.id == id).first()
    if not db_funcionario:
        db.close()
        raise HTTPException(status_code=404, detail='Funcionário não encontrado')
    
    # Só atualiza campos que foram enviados e não estão vazios
    if funcionario.nome and funcionario.nome.strip():
        db_funcionario.nome = funcionario.nome
    if funcionario.sobrenome and funcionario.sobrenome.strip():
        db_funcionario.sobrenome = funcionario.sobrenome
    if funcionario.celular is not None and funcionario.celular != '':
        db_funcionario.celular = funcionario.celular
    if funcionario.email is not None and funcionario.email != '':
        db_funcionario.email = funcionario.email
    if funcionario.cpf is not None and funcionario.cpf != '':
        db_funcionario.cpf = funcionario.cpf
    if funcionario.tipo_contrato is not None and funcionario.tipo_contrato != '':
        db_funcionario.tipo_contrato = funcionario.tipo_contrato
    
    # Atualiza vínculo de cargo - prioriza campos separados se fornecidos
    cargo_obj = None
    
    # Se foram fornecidos campos separados, usa eles (prioridade)
    if any([funcionario.cargo_nome, funcionario.cargo_funcao, funcionario.cargo_equipe, funcionario.cargo_nivel]):
        # Busca cargo existente com esses atributos
        query = db.query(Cargo)
        if funcionario.cargo_nome:
            query = query.filter(Cargo.nome == funcionario.cargo_nome)
        if funcionario.cargo_funcao:
            query = query.filter(Cargo.funcao == funcionario.cargo_funcao)
        if funcionario.cargo_equipe:
            query = query.filter(Cargo.equipe == funcionario.cargo_equipe)
        if funcionario.cargo_nivel:
            query = query.filter(Cargo.nivel == funcionario.cargo_nivel)
            
        cargo_obj = query.first()
        
        # Se não encontrou, cria novo cargo
        if not cargo_obj:
            cargo_obj = Cargo(
                nome=funcionario.cargo_nome,
                funcao=funcionario.cargo_funcao,
                equipe=funcionario.cargo_equipe,
                nivel=funcionario.cargo_nivel
            )
            db.add(cargo_obj)
            db.flush()
            db.refresh(cargo_obj)
    
    # Caso contrário, se foi fornecido cargo_id, usa ele
    elif funcionario.cargo_id:
        cargo_obj = db.query(Cargo).filter(Cargo.id == funcionario.cargo_id).first()
    
    # Se encontrou ou criou um cargo, cria o vínculo
    if cargo_obj:
        dt_inicio = date.today()
        
        # Verifica se já existe um vínculo ativo com o mesmo cargo
        vinculo_ativo_existente = db.query(FuncionarioCargo).filter_by(
            funcionario_id=db_funcionario.id,
            cargo_id=cargo_obj.id,
            dt_fim=None
        ).first()
        
        if not vinculo_ativo_existente:
            # SIMPLIFICADO: apenas insere - o trigger do banco cuida do fechamento
            novo_vinculo = FuncionarioCargo(
                funcionario_id=db_funcionario.id,
                cargo_id=cargo_obj.id,
                dt_inicio=dt_inicio,
                cargo_nome=cargo_obj.nome,
                cargo_nivel=getattr(cargo_obj, 'nivel', None),
                cargo_funcao=getattr(cargo_obj, 'funcao', None),
                cargo_equipe=getattr(cargo_obj, 'equipe', None)
            )
            db.add(novo_vinculo)
            db.flush()
    
    # Só atualiza datas se foram fornecidas e não estão vazias
    if hasattr(funcionario, 'data_admissao') and funcionario.data_admissao not in ('', None):
        db_funcionario.data_admissao = str(funcionario.data_admissao)
    
    if hasattr(funcionario, 'data_afastamento') and funcionario.data_afastamento not in ('', None):
        db_funcionario.data_afastamento = converter_string_para_date(funcionario.data_afastamento)
    
    if hasattr(funcionario, 'data_retorno') and funcionario.data_retorno not in ('', None):
        db_funcionario.data_retorno = converter_string_para_date(funcionario.data_retorno)
    
    if hasattr(funcionario, 'motivo_afastamento') and funcionario.motivo_afastamento not in ('', None):
        db_funcionario.motivo_afastamento = funcionario.motivo_afastamento
    
    if hasattr(funcionario, 'data_inativado') and funcionario.data_inativado not in ('', None):
        db_funcionario.data_inativado = str(funcionario.data_inativado)
    
    # Atualiza relacionamentos apenas se fornecidos
    # Só atualiza relacionamentos se foram explicitamente fornecidos
    if funcionario.grupos_email_ids is not None:
        if funcionario.grupos_email_ids:
            grupos = db.query(GrupoEmail).filter(GrupoEmail.id.in_(funcionario.grupos_email_ids)).all()
            db_funcionario.grupos_email = grupos
        else:
            db_funcionario.grupos_email = []
    
    if hasattr(funcionario, 'grupos_pasta_ids') and funcionario.grupos_pasta_ids is not None:
        if funcionario.grupos_pasta_ids:
            grupos_pasta = db.query(GrupoPasta).filter(GrupoPasta.id.in_(funcionario.grupos_pasta_ids)).all()
            db_funcionario.grupos_pasta = grupos_pasta
        else:
            db_funcionario.grupos_pasta = []
    
    if funcionario.setores_ids is not None:
        if funcionario.setores_ids:
            setores = db.query(Setor).filter(Setor.id.in_(funcionario.setores_ids)).all()
            db_funcionario.setores = setores
        else:
            db_funcionario.setores = []
    
    if funcionario.sistemas_ids is not None:
        if funcionario.sistemas_ids:
            sistemas = db.query(SistemaModel).filter(SistemaModel.id.in_(funcionario.sistemas_ids)).all()
            db_funcionario.sistemas = sistemas
        else:
            db_funcionario.sistemas = []
    # Atualiza meta e tipo_pgto
    if hasattr(funcionario, 'meta') and funcionario.meta is not None and hasattr(funcionario, 'tipo_pgto') and funcionario.tipo_pgto is not None:
        try:
            # Converte meta para float se for string
            meta_valor = float(funcionario.meta) if isinstance(funcionario.meta, str) else funcionario.meta
            
            # Busca meta existente ou cria nova
            meta_obj = db.query(Meta).filter_by(calc_meta=meta_valor, tipo_pgto=funcionario.tipo_pgto).first()
            if not meta_obj:
                meta_obj = Meta(calc_meta=meta_valor, tipo_pgto=funcionario.tipo_pgto)
                db.add(meta_obj)
                db.flush()  # Usa flush ao invés de commit
                db.refresh(meta_obj)
            
            # Verifica se já existe vínculo ativo com a mesma meta
            dt_inicio = date.today()
            
            # Busca vínculo ativo existente com a mesma meta
            vinculo_meta_existente = db.query(FuncionarioMeta).filter_by(
                funcionario_id=db_funcionario.id,
                meta_id=meta_obj.id,
                dt_fim=None
            ).first()
            
            if not vinculo_meta_existente:
                # SIMPLIFICADO: apenas insere - o trigger do banco cuida do fechamento
                novo_vinculo = FuncionarioMeta(
                    funcionario_id=db_funcionario.id, 
                    meta_id=meta_obj.id, 
                    dt_inicio=dt_inicio
                )
                db.add(novo_vinculo)
                db.flush()
        except (ValueError, TypeError) as e:
            db.close()
            raise HTTPException(status_code=422, detail=f"Valor de meta inválido: {funcionario.meta}. Deve ser um número (0, 0.5 ou 1).")
        except Exception as e:
            db.rollback()
            db.close()
            raise HTTPException(status_code=500, detail=f"Erro ao processar meta: {str(e)}")
    db.commit()
    db.refresh(db_funcionario)
    cargo_nome = None
    if hasattr(db_funcionario, 'cargos_vinculos') and db_funcionario.cargos_vinculos:
        vinculos_ativos = [v for v in db_funcionario.cargos_vinculos if v.dt_fim is None]
        if vinculos_ativos:
            cargo_nome = vinculos_ativos[0].cargo.nome
        else:
            vinculo_recente = max(db_funcionario.cargos_vinculos, key=lambda v: v.dt_inicio or date.min)
            cargo_nome = vinculo_recente.cargo.nome
    funcionario_schema = FuncionarioSchema.model_validate({
        **db_funcionario.__dict__,
        'setores': [SetorOut.from_orm(setor) for setor in db_funcionario.setores],
        'sistemas': [SistemaSchema.from_orm(sistema) for sistema in db_funcionario.sistemas],
        'grupos_email': [GrupoEmailOut.from_orm(grupo) for grupo in db_funcionario.grupos_email],
        'grupos_pasta': [GrupoPastaOut.from_orm(grupo) for grupo in db_funcionario.grupos_pasta],
        'cargo': cargo_nome,
        'data_admissao': str(db_funcionario.data_admissao) if db_funcionario.data_admissao else '',
        'data_inativado': str(db_funcionario.data_inativado) if db_funcionario.data_inativado is not None else '',
        'cpf': db_funcionario.cpf,
        'data_afastamento': str(db_funcionario.data_afastamento) if db_funcionario.data_afastamento else None,
        'tipo_contrato': db_funcionario.tipo_contrato,
        'data_retorno': str(db_funcionario.data_retorno) if db_funcionario.data_retorno else None
    })
    db.close()
    return funcionario_schema

@router.get('/funcionarios/', response_model=list[FuncionarioSchema])
def list_funcionarios():
    db = SessionLocal()
    from sqlalchemy.orm import joinedload
    funcionarios = db.query(FuncionarioModel).options(
        joinedload(FuncionarioModel.setores),
        joinedload(FuncionarioModel.sistemas),
        joinedload(FuncionarioModel.grupos_email),
        joinedload(FuncionarioModel.grupos_pasta),
        joinedload(FuncionarioModel.cargos_vinculos).joinedload(FuncionarioCargo.cargo)
    ).all()
    resultado = []
    for funcionario in funcionarios:
        setores = [SetorOut.from_orm(setor) for setor in funcionario.setores]
        sistemas = [SistemaSchema.from_orm(sistema) for sistema in funcionario.sistemas]
        grupos_email = [GrupoEmailOut.from_orm(grupo) for grupo in funcionario.grupos_email]
        grupos_pasta = [GrupoPastaOut.from_orm(grupo) for grupo in funcionario.grupos_pasta]
        cargo_nome = None
        if hasattr(funcionario, 'cargos_vinculos') and funcionario.cargos_vinculos:
            vinculos_ativos = [v for v in funcionario.cargos_vinculos if v.dt_fim is None]
            if vinculos_ativos:
                cargo_nome = vinculos_ativos[0].cargo.nome
            else:
                vinculo_recente = max(funcionario.cargos_vinculos, key=lambda v: v.dt_inicio or date.min)
                cargo_nome = vinculo_recente.cargo.nome
        funcionario_schema = FuncionarioSchema.model_validate({
            **funcionario.__dict__,
            'setores': setores,
            'sistemas': sistemas,
            'grupos_email': grupos_email,
            'grupos_pasta': grupos_pasta,
            'cargo': cargo_nome,
            'data_admissao': str(funcionario.data_admissao) if funcionario.data_admissao not in (None, '') else '',
            'data_inativado': str(funcionario.data_inativado) if funcionario.data_inativado is not None else '',
            'cpf': funcionario.cpf,
            'data_afastamento': funcionario.data_afastamento.strftime('%Y-%m-%d') if funcionario.data_afastamento else None,
            'tipo_contrato': funcionario.tipo_contrato,
            'data_retorno': funcionario.data_retorno.strftime('%Y-%m-%d') if funcionario.data_retorno else None,
            'motivo_afastamento': funcionario.motivo_afastamento
        })
        resultado.append(funcionario_schema)
    db.close()
    return resultado

@router.delete('/funcionarios/{id}')
def excluir_funcionario(id: int):
    db = SessionLocal()
    funcionario = db.query(FuncionarioModel).filter(FuncionarioModel.id == id).first()
    if not funcionario:
        db.close()
        raise HTTPException(status_code=404, detail='Funcionário não encontrado')
    # Remove vínculos de cargo
    db.query(FuncionarioCargo).filter(FuncionarioCargo.funcionario_id == id).delete()
    # Remove vínculos de setores, sistemas, grupos de email, grupos de pasta
    funcionario.setores.clear()
    funcionario.sistemas.clear()
    funcionario.grupos_email.clear()
    funcionario.grupos_pasta.clear()
    db.delete(funcionario)
    db.commit()
    db.close()
    return {'ok': True}

