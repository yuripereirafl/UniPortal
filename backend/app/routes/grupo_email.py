from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import sessionmaker
from app.models.grupo_email import GrupoEmail
from app.schemas.grupo_email import GrupoEmailCreate, GrupoEmailOut
from app.database import engine

router = APIRouter()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@router.get('/grupos-email/', response_model=list[GrupoEmailOut])
def list_grupos_email():
    db = SessionLocal()
    grupos = db.query(GrupoEmail).all()
    db.close()
    return grupos

@router.post('/grupos-email/', response_model=GrupoEmailOut)
def criar_grupo_email(grupo: GrupoEmailCreate):
    db = SessionLocal()
    novo = GrupoEmail(nome=grupo.nome)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    db.close()
    return novo

@router.put('/grupos-email/{id}', response_model=GrupoEmailOut)
def editar_grupo_email(id: int, grupo: GrupoEmailCreate):
    db = SessionLocal()
    db_grupo = db.query(GrupoEmail).filter(GrupoEmail.id == id).first()
    if not db_grupo:
        db.close()
        raise HTTPException(status_code=404, detail='Grupo não encontrado')
    db_grupo.nome = grupo.nome
    db.commit()
    db.refresh(db_grupo)
    db.close()
    return db_grupo

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
