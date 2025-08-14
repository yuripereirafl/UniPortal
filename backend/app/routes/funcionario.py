from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from ..models.funcionario import Funcionario as FuncionarioModel
from ..models.setor import Setor
from ..models.sistema import Sistema as SistemaModel
from ..models.grupo_email import GrupoEmail
from ..models.grupo_pasta import GrupoPasta
from ..schemas.funcionario import FuncionarioCreate, Funcionario as FuncionarioSchema
from ..schemas.sistema import Sistema as SistemaSchema
from ..schemas.setor import SetorOut
from ..schemas.grupo_email import GrupoEmailOut
from ..schemas.grupo_pasta import GrupoPastaOut
from ..database import engine
from ..models.user import User
from ..dependencies import get_current_user, has_permission

router = APIRouter()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@router.post('/funcionarios/', response_model=FuncionarioSchema)
def adicionar_funcionario(funcionario: FuncionarioCreate, current_user: User = Depends(get_current_user)):
    # Verificar permissões do usuário
    db = SessionLocal()
    if not has_permission(current_user, "ALTERAR_TUDO", db):
        db.close()
        raise HTTPException(status_code=403, detail="Permissão negada")
    db = SessionLocal()
    print(f"[LOG] Valor recebido para data_admissao: {funcionario.data_admissao} (type: {type(funcionario.data_admissao)})")
    # Aceita data_admissao no formato 'YYYY-MM-DD' e salva como string
    data_admissao = ''
    if hasattr(funcionario, 'data_admissao') and funcionario.data_admissao:
        # Se vier no formato 'YYYY-MM-DD', usa direto, sem conversão
        if isinstance(funcionario.data_admissao, str) and len(funcionario.data_admissao) == 10 and funcionario.data_admissao[4] == '-':
            data_admissao = funcionario.data_admissao
        else:
            # Se vier como datetime ou outro formato, converte para string
            data_admissao = str(funcionario.data_admissao)
    else:
        data_admissao = str(datetime.now().date())
    print(f"[LOG] Valor processado para data_admissao (antes de salvar): {data_admissao} (type: {type(data_admissao)})")
    # Convertendo strings vazias para None antes de salvar no banco
    data_afastamento = funcionario.data_afastamento if funcionario.data_afastamento else None
    data_retorno = funcionario.data_retorno if funcionario.data_retorno else None
    data_inativado = funcionario.data_inativado if funcionario.data_inativado else None

    novo_funcionario = FuncionarioModel(
        nome=funcionario.nome,
        sobrenome=funcionario.sobrenome,
        cargo=funcionario.cargo,
        celular=funcionario.celular,
        email=funcionario.email,
        cpf=funcionario.cpf,  # Novo campo
        data_afastamento=data_afastamento,  # Atualizado
        tipo_contrato=funcionario.tipo_contrato,  # Novo campo
        data_retorno=data_retorno,  # Atualizado
        data_admissao=data_admissao,
        data_inativado=data_inativado  # Atualizado
    )
    print(f"[LOG] Valor salvo no banco para data_admissao: {novo_funcionario.data_admissao} (type: {type(novo_funcionario.data_admissao)})")
    db.add(novo_funcionario)
    db.commit()
    db.refresh(novo_funcionario)
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
        # Vincula grupos do usuário (via usuario_grupo)
        if hasattr(funcionario, 'grupos_ids') and funcionario.grupos_ids:
            from app.models.grupos import Grupo
            usuario = db.query(User).filter(User.id_funcionario == novo_funcionario.id).first()
            if usuario:
                grupos_usuario = db.query(Grupo).filter(Grupo.id.in_(funcionario.grupos_ids)).all()
                usuario.grupos = grupos_usuario
                db.commit()
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
        'data_admissao': str(novo_funcionario.data_admissao) if novo_funcionario.data_admissao is not None else '',
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
def atualizar_funcionario(id: int, funcionario: FuncionarioCreate, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    db_funcionario = db.query(FuncionarioModel).filter(FuncionarioModel.id == id).first()
    if not db_funcionario:
        db.close()
        raise HTTPException(status_code=404, detail='Funcionário não encontrado')

    # Verificar permissões do usuário
    if not has_permission(current_user, "ALTERAR_TUDO", db):
        db.close()
        raise HTTPException(status_code=403, detail="Permissão negada")

    # Validação de campos de data
    try:
        db_funcionario.data_afastamento = funcionario.data_afastamento if funcionario.data_afastamento else None
        db_funcionario.data_retorno = funcionario.data_retorno if funcionario.data_retorno else None
        db_funcionario.data_inativado = funcionario.data_inativado if funcionario.data_inativado else None
    except ValueError:
        db.close()
        raise HTTPException(status_code=400, detail="Formato de data inválido")

    # Atualizar outros campos
    db_funcionario.nome = funcionario.nome
    db_funcionario.sobrenome = funcionario.sobrenome
    db_funcionario.cargo = funcionario.cargo
    db_funcionario.celular = funcionario.celular
    db_funcionario.email = funcionario.email
    db_funcionario.cpf = funcionario.cpf
    db_funcionario.tipo_contrato = funcionario.tipo_contrato

    # Atualiza grupos de e-mail
    if funcionario.grupos_email_ids:
        grupos = db.query(GrupoEmail).filter(GrupoEmail.id.in_(funcionario.grupos_email_ids)).all()
        db_funcionario.grupos_email = grupos
    else:
        db_funcionario.grupos_email = []

    # Atualiza grupos de pasta
    if hasattr(funcionario, 'grupos_pasta_ids') and funcionario.grupos_pasta_ids:
        grupos_pasta = db.query(GrupoPasta).filter(GrupoPasta.id.in_(funcionario.grupos_pasta_ids)).all()
        db_funcionario.grupos_pasta = grupos_pasta
    else:
        db_funcionario.grupos_pasta = []

    # Atualiza setores
    if funcionario.setores_ids:
        setores = db.query(Setor).filter(Setor.id.in_(funcionario.setores_ids)).all()
        db_funcionario.setores = setores

    db.commit()
    # Recarrega o objeto com os relacionamentos para evitar DetachedInstanceError
    from sqlalchemy.orm import selectinload
    funcionario_atualizado = db.query(FuncionarioModel).options(
        selectinload(FuncionarioModel.setores),
        selectinload(FuncionarioModel.sistemas),
        selectinload(FuncionarioModel.grupos_email),
        selectinload(FuncionarioModel.grupos_pasta)
    ).filter(FuncionarioModel.id == id).first()
    # Serializa data_admissao para string se necessário
    if funcionario_atualizado and funcionario_atualizado.data_admissao and not isinstance(funcionario_atualizado.data_admissao, str):
        funcionario_atualizado.data_admissao = funcionario_atualizado.data_admissao.isoformat()
    db.close()
    return funcionario_atualizado

@router.get('/funcionarios/', response_model=list[FuncionarioSchema])
def list_funcionarios():
    db = SessionLocal()
    funcionarios = db.query(FuncionarioModel).all()
    resultado = []
    for funcionario in funcionarios:
        setores = [SetorOut.from_orm(setor) for setor in funcionario.setores]
        sistemas = [SistemaSchema.from_orm(sistema) for sistema in funcionario.sistemas]
        grupos_email = [GrupoEmailOut.from_orm(grupo) for grupo in funcionario.grupos_email]
        grupos_pasta = [GrupoPastaOut.from_orm(grupo) for grupo in funcionario.grupos_pasta]
        funcionario_schema = FuncionarioSchema.model_validate({
            **funcionario.__dict__,
            'setores': setores,
            'sistemas': sistemas,
            'grupos_email': grupos_email,
            'grupos_pasta': grupos_pasta,
            'data_admissao': str(funcionario.data_admissao) if funcionario.data_admissao is not None else '',
            'data_inativado': str(funcionario.data_inativado) if funcionario.data_inativado is not None else '',
            'cpf': funcionario.cpf,
            'data_afastamento': str(funcionario.data_afastamento) if funcionario.data_afastamento else None,
            'tipo_contrato': funcionario.tipo_contrato,
            'data_retorno': str(funcionario.data_retorno) if funcionario.data_retorno else None
        })
        resultado.append(funcionario_schema)
    db.close()
    return resultado

@router.delete('/funcionarios/{id}')
def excluir_funcionario(id: int, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    if not has_permission(current_user, "ALTERAR_TUDO", db):
        db.close()
        raise HTTPException(status_code=403, detail="Permissão negada")
    db = SessionLocal()
    db_funcionario = db.query(FuncionarioModel).filter(FuncionarioModel.id == id).first()
    if not db_funcionario:
        db.close()
        raise HTTPException(status_code=404, detail='Funcionário não encontrado')
    db.delete(db_funcionario)
    db.commit()
    db.close()
    return {'ok': True}

