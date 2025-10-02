from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.models.setor import Setor
from backend.app.schemas.setor import SetorCreate, SetorUpdate, SetorOut
from app.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/setores/', response_model=list[SetorOut])
def listar_setores(db: Session = Depends(get_db)):
    return db.query(Setor).all()

@router.post('/setores/', response_model=SetorOut)
def criar_setor(setor: SetorCreate, db: Session = Depends(get_db)):
    db_setor = Setor(**setor.dict())
    db.add(db_setor)
    db.commit()
    db.refresh(db_setor)
    return db_setor

@router.put('/setores/{setor_id}', response_model=SetorOut)
def atualizar_setor(setor_id: int, setor: SetorUpdate, db: Session = Depends(get_db)):
    db_setor = db.query(Setor).filter(Setor.id == setor_id).first()
    if not db_setor:
        raise HTTPException(status_code=404, detail='Setor não encontrado')
    for key, value in setor.dict(exclude_unset=True).items():
        setattr(db_setor, key, value)
    db.commit()
    db.refresh(db_setor)
    return db_setor

@router.delete('/setores/{setor_id}')
def excluir_setor(setor_id: int, db: Session = Depends(get_db)):
    db_setor = db.query(Setor).filter(Setor.id == setor_id).first()
    if not db_setor:
        raise HTTPException(status_code=404, detail='Setor não encontrado')
    db.delete(db_setor)
    db.commit()
    return {'ok': True}
