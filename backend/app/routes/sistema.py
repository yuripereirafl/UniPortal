from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.sistema import Sistema  # modelo SQLAlchemy
from ..schemas.sistema import SistemaCreate, Sistema as SistemaSchema  # schema Pydantic
from ..database import SessionLocal, engine
from sqlalchemy.orm import sessionmaker

router = APIRouter()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@router.post('/sistemas/', response_model=SistemaSchema)
def create_sistema(sistema: SistemaCreate):
    db = SessionLocal()
    db_sistema = Sistema(**sistema.dict())
    db.add(db_sistema)
    db.commit()
    db.refresh(db_sistema)
    db.close()
    return db_sistema

@router.get('/sistemas/', response_model=list[SistemaSchema])
def list_sistemas():
    db = SessionLocal()
    sistemas = db.query(Sistema).all()
    db.close()
    return sistemas

@router.put('/sistemas/{id}', response_model=SistemaSchema)
def update_sistema(id: int, sistema: SistemaCreate):
    db = SessionLocal()
    db_sistema = db.query(Sistema).filter(Sistema.id == id).first()
    if not db_sistema:
        db.close()
        raise HTTPException(status_code=404, detail='Sistema não encontrado')
    db_sistema.nome = sistema.nome
    db_sistema.descricao = sistema.descricao
    db_sistema.status = sistema.status
    db.commit()
    db.refresh(db_sistema)
    db.close()
    return db_sistema

@router.delete('/sistemas/{id}')
def delete_sistema(id: int):
    db = SessionLocal()
    db_sistema = db.query(Sistema).filter(Sistema.id == id).first()
    if not db_sistema:
        db.close()
        raise HTTPException(status_code=404, detail='Sistema não encontrado')
    db.delete(db_sistema)
    db.commit()
    db.close()
    return {"ok": True}
