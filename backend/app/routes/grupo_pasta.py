from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from app.models.grupo_pasta import GrupoPasta
from app.schemas.grupo_pasta import GrupoPastaCreate, GrupoPastaOut
from app.database import engine

router = APIRouter()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@router.get('/grupos-pasta/', response_model=list[GrupoPastaOut])
def list_grupos_pasta():
    db = SessionLocal()
    grupos = db.query(GrupoPasta).all()
    db.close()
    return grupos

@router.post('/grupos-pasta/', response_model=GrupoPastaOut)
def criar_grupo_pasta(grupo: GrupoPastaCreate):
    db = SessionLocal()
    novo = GrupoPasta(nome=grupo.nome, descricao=grupo.descricao)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    db.close()
    return novo

@router.put('/grupos-pasta/{id}', response_model=GrupoPastaOut)
def editar_grupo_pasta(id: int, grupo: GrupoPastaCreate):
    db = SessionLocal()
    grupo_db = db.query(GrupoPasta).filter(GrupoPasta.id == id).first()
    if not grupo_db:
        db.close()
        raise HTTPException(status_code=404, detail='Grupo de pasta não encontrado')
    grupo_db.nome = grupo.nome
    grupo_db.descricao = grupo.descricao
    db.commit()
    db.refresh(grupo_db)
    db.close()
    return grupo_db

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
