from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import sessionmaker, joinedload
from app.models.grupo_email import GrupoEmail
from app.schemas.grupo_email import GrupoEmailCreate, GrupoEmailOut
from app.database import engine
from app.models.funcionario import Funcionario
from fastapi import status

router = APIRouter()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@router.get('/grupos-email/')
def list_grupos_email():
    db = SessionLocal()
    # pré-carrega relação funcionarios para evitar lazy-load após fechar sessão
    grupos = db.query(GrupoEmail).options(joinedload(GrupoEmail.funcionarios)).all()
    def _serialize_grupo(g):
        funcionarios = []
        for f in (g.funcionarios or []):
            funcionarios.append({'id': f.id, 'nome': f.nome, 'sobrenome': f.sobrenome, 'email': f.email})
        return {'id': g.id, 'nome': g.nome, 'funcionarios': funcionarios, 'qtd_participantes': len(funcionarios)}

    result = [_serialize_grupo(g) for g in grupos]
    db.close()
    return JSONResponse(content=result)

@router.post('/grupos-email/')
def criar_grupo_email(grupo: GrupoEmailCreate):
    db = SessionLocal()
    novo = GrupoEmail(nome=grupo.nome)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    # Serializa resposta incluindo participantes e contagem (inicialmente vazia)
    funcionarios = [{'id': f.id, 'nome': f.nome, 'sobrenome': f.sobrenome, 'email': f.email} for f in (novo.funcionarios or [])]
    result = {'id': novo.id, 'nome': novo.nome, 'funcionarios': funcionarios, 'qtd_participantes': len(funcionarios)}
    db.close()
    return JSONResponse(content=result)

@router.put('/grupos-email/{id}')
def editar_grupo_email(id: int, grupo: GrupoEmailCreate):
    db = SessionLocal()
    db_grupo = db.query(GrupoEmail).filter(GrupoEmail.id == id).first()
    if not db_grupo:
        db.close()
        raise HTTPException(status_code=404, detail='Grupo não encontrado')
    db_grupo.nome = grupo.nome
    db.commit()
    # Recarrega com participantes para serializar corretamente
    db.refresh(db_grupo)
    grupo_completo = db.query(GrupoEmail).options(joinedload(GrupoEmail.funcionarios)).filter(GrupoEmail.id == id).first()
    funcionarios = [{'id': f.id, 'nome': f.nome, 'sobrenome': f.sobrenome, 'email': f.email} for f in (grupo_completo.funcionarios or [])]
    result = {'id': grupo_completo.id, 'nome': grupo_completo.nome, 'funcionarios': funcionarios, 'qtd_participantes': len(funcionarios)}
    db.close()
    return JSONResponse(content=result)

@router.delete('/grupos-email/{id}')
def excluir_grupo_email(id: int):
    db = SessionLocal()
    db_grupo = db.query(GrupoEmail).filter(GrupoEmail.id == id).first()
    if not db_grupo:
        db.close()
        raise HTTPException(status_code=404, detail='Grupo não encontrado')
    db.delete(db_grupo)
    db.commit()
    db.close()
    return {'ok': True}


@router.get('/grupos-email/{id}')
def obter_grupo_email(id: int):
    db = SessionLocal()
    grupo = db.query(GrupoEmail).options(joinedload(GrupoEmail.funcionarios)).filter(GrupoEmail.id == id).first()
    if not grupo:
        db.close()
        raise HTTPException(status_code=404, detail='Grupo não encontrado')
    funcionarios = [{'id': f.id, 'nome': f.nome, 'sobrenome': f.sobrenome, 'email': f.email} for f in (grupo.funcionarios or [])]
    result = {
        'id': grupo.id,
        'nome': grupo.nome,
        'funcionarios': funcionarios,
        'qtd_participantes': len(funcionarios)
    }
    db.close()
    return JSONResponse(content=result)


@router.get('/grupos-email/{id}/disponiveis')
def funcionarios_disponiveis_email(id: int):
    """Retorna funcionários que não fazem parte do grupo (para seleção no modal)."""
    db = SessionLocal()
    grupo = db.query(GrupoEmail).options(joinedload(GrupoEmail.funcionarios)).filter(GrupoEmail.id == id).first()
    if not grupo:
        db.close()
        raise HTTPException(status_code=404, detail='Grupo não encontrado')

    # Pegar todos os funcionários e filtrar os que já estão no grupo
    todos = db.query(Funcionario).all()
    participantes_ids = {f.id for f in grupo.funcionarios}
    disponiveis = [f for f in todos if f.id not in participantes_ids]
    funcionarios = [{'id': f.id, 'nome': f.nome, 'sobrenome': f.sobrenome, 'email': f.email} for f in disponiveis]
    db.close()
    # Retornar lista compatível com frontend (array direto)
    return funcionarios


@router.post('/grupos-email/{id}/adicionar-participante/{funcionario_id}', status_code=status.HTTP_200_OK)
def adicionar_participante_email(id: int, funcionario_id: int):
    db = SessionLocal()
    grupo = db.query(GrupoEmail).filter(GrupoEmail.id == id).first()
    funcionario = db.query(Funcionario).filter(Funcionario.id == funcionario_id).first()
    if not grupo or not funcionario:
        db.close()
        raise HTTPException(status_code=404, detail='Grupo ou funcionário não encontrado')

    participantes_ids = {f.id for f in (grupo.funcionarios or [])}
    if funcionario.id not in participantes_ids:
        grupo.funcionarios.append(funcionario)
        db.commit()
        db.refresh(grupo)
    else:
        db.close()
        raise HTTPException(status_code=409, detail='Funcionário já é participante do grupo')

    funcionarios = [{'id': f.id, 'nome': f.nome, 'sobrenome': f.sobrenome, 'email': f.email} for f in (grupo.funcionarios or [])]
    result = {'funcionarios': funcionarios, 'qtd_participantes': len(funcionarios)}
    db.close()
    return JSONResponse(content=result)


@router.delete('/grupos-email/{id}/remover-participante/{funcionario_id}', status_code=status.HTTP_200_OK)
def remover_participante_email(id: int, funcionario_id: int):
    db = SessionLocal()
    grupo = db.query(GrupoEmail).filter(GrupoEmail.id == id).first()
    funcionario = db.query(Funcionario).filter(Funcionario.id == funcionario_id).first()
    if not grupo or not funcionario:
        db.close()
        raise HTTPException(status_code=404, detail='Grupo ou funcionário não encontrado')

    participantes_ids = {f.id for f in (grupo.funcionarios or [])}
    if funcionario.id in participantes_ids:
        # remove pelo id para evitar problemas de identidade
        grupo.funcionarios = [f for f in grupo.funcionarios if f.id != funcionario.id]
        db.commit()
        db.refresh(grupo)
    else:
        db.close()
        raise HTTPException(status_code=404, detail='Funcionário não é participante do grupo')

    funcionarios = [{'id': f.id, 'nome': f.nome, 'sobrenome': f.sobrenome, 'email': f.email} for f in (grupo.funcionarios or [])]
    result = {'funcionarios': funcionarios, 'qtd_participantes': len(funcionarios)}
    db.close()
    return JSONResponse(content=result)
