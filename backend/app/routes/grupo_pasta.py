from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker, joinedload
from app.models.grupo_pasta import GrupoPasta
from app.schemas.grupo_pasta import GrupoPastaCreate, GrupoPastaOut
from app.database import engine
from app.models.funcionario import Funcionario
from fastapi import status

router = APIRouter()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@router.get('/grupos-pasta/')
def list_grupos_pasta():
    db = SessionLocal()
    grupos = db.query(GrupoPasta).options(joinedload(GrupoPasta.funcionarios)).all()
    def _serialize_grupo(g):
        funcionarios = []
        for f in (g.funcionarios or []):
            funcionarios.append({'id': f.id, 'nome': f.nome, 'sobrenome': f.sobrenome, 'email': f.email})
        return {'id': g.id, 'nome': g.nome, 'descricao': g.descricao, 'funcionarios': funcionarios, 'qtd_participantes': len(funcionarios)}

    result = [_serialize_grupo(g) for g in grupos]
    db.close()
    return JSONResponse(content=result)

@router.post('/grupos-pasta/')
def criar_grupo_pasta(grupo: GrupoPastaCreate):
    db = SessionLocal()
    novo = GrupoPasta(nome=grupo.nome, descricao=grupo.descricao)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    funcionarios = [{'id': f.id, 'nome': f.nome, 'sobrenome': f.sobrenome, 'email': f.email} for f in (novo.funcionarios or [])]
    result = {'id': novo.id, 'nome': novo.nome, 'descricao': novo.descricao, 'funcionarios': funcionarios, 'qtd_participantes': len(funcionarios)}
    db.close()
    return JSONResponse(content=result)

@router.put('/grupos-pasta/{id}')
def editar_grupo_pasta(id: int, grupo: GrupoPastaCreate):
    db = SessionLocal()
    grupo_db = db.query(GrupoPasta).filter(GrupoPasta.id == id).first()
    if not grupo_db:
        db.close()
        raise HTTPException(status_code=404, detail='Grupo de pasta não encontrado')
    grupo_db.nome = grupo.nome
    grupo_db.descricao = grupo.descricao
    db.commit()
    # Recarrega com participantes para serializar corretamente
    db.refresh(grupo_db)
    grupo_completo = db.query(GrupoPasta).options(joinedload(GrupoPasta.funcionarios)).filter(GrupoPasta.id == id).first()
    funcionarios = [{'id': f.id, 'nome': f.nome, 'sobrenome': f.sobrenome, 'email': f.email} for f in (grupo_completo.funcionarios or [])]
    result = {'id': grupo_completo.id, 'nome': grupo_completo.nome, 'descricao': grupo_completo.descricao, 'funcionarios': funcionarios, 'qtd_participantes': len(funcionarios)}
    db.close()
    return JSONResponse(content=result)

@router.delete('/grupos-pasta/{id}')
def excluir_grupo_pasta(id: int):
    db = SessionLocal()
    grupo = db.query(GrupoPasta).filter(GrupoPasta.id == id).first()
    if not grupo:
        db.close()
        raise HTTPException(status_code=404, detail='Grupo de pasta não encontrado')
    db.delete(grupo)
    db.commit()
    db.close()
    return {'ok': True}


@router.get('/grupos-pasta/{id}')
def obter_grupo_pasta(id: int):
    db = SessionLocal()
    grupo = db.query(GrupoPasta).options(joinedload(GrupoPasta.funcionarios)).filter(GrupoPasta.id == id).first()
    if not grupo:
        db.close()
        raise HTTPException(status_code=404, detail='Grupo de pasta não encontrado')
    funcionarios = [{'id': f.id, 'nome': f.nome, 'sobrenome': f.sobrenome, 'email': f.email} for f in (grupo.funcionarios or [])]
    result = {'id': grupo.id, 'nome': grupo.nome, 'descricao': grupo.descricao, 'funcionarios': funcionarios, 'qtd_participantes': len(funcionarios)}
    db.close()
    return JSONResponse(content=result)


@router.get('/grupos-pasta/{id}/disponiveis')
def funcionarios_disponiveis_pasta(id: int):
    db = SessionLocal()
    grupo = db.query(GrupoPasta).options(joinedload(GrupoPasta.funcionarios)).filter(GrupoPasta.id == id).first()
    if not grupo:
        db.close()
        raise HTTPException(status_code=404, detail='Grupo de pasta não encontrado')

    todos = db.query(Funcionario).all()
    participantes_ids = {f.id for f in grupo.funcionarios}
    disponiveis = [f for f in todos if f.id not in participantes_ids]
    funcionarios = [{'id': f.id, 'nome': f.nome, 'sobrenome': f.sobrenome, 'email': f.email} for f in disponiveis]
    db.close()
    return funcionarios


@router.post('/grupos-pasta/{id}/adicionar-participante/{funcionario_id}', status_code=status.HTTP_200_OK)
def adicionar_participante_pasta(id: int, funcionario_id: int):
    db = SessionLocal()
    grupo = db.query(GrupoPasta).filter(GrupoPasta.id == id).first()
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


@router.delete('/grupos-pasta/{id}/remover-participante/{funcionario_id}', status_code=status.HTTP_200_OK)
def remover_participante_pasta(id: int, funcionario_id: int):
    db = SessionLocal()
    grupo = db.query(GrupoPasta).filter(GrupoPasta.id == id).first()
    funcionario = db.query(Funcionario).filter(Funcionario.id == funcionario_id).first()
    if not grupo or not funcionario:
        db.close()
        raise HTTPException(status_code=404, detail='Grupo ou funcionário não encontrado')

    participantes_ids = {f.id for f in (grupo.funcionarios or [])}
    if funcionario.id in participantes_ids:
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
