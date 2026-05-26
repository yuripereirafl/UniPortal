from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db
from app.models.dominio import Dominio
from app.schemas.dominio import DominioCreate, DominioUpdate, DominioResponse

router = APIRouter()

@router.get("/", response_model=List[DominioResponse])
def get_dominios(db: Session = Depends(get_db)):
    return db.query(Dominio).all()

@router.post("/", response_model=DominioResponse)
def create_dominio(dominio: DominioCreate, db: Session = Depends(get_db)):
    db_dominio = Dominio(**dominio.dict())
    try:
        db.add(db_dominio)
        db.commit()
        db.refresh(db_dominio)
        return db_dominio
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Este domínio já está cadastrado no sistema.")

@router.put("/{dominio_id}", response_model=DominioResponse)
def update_dominio(dominio_id: int, dominio: DominioUpdate, db: Session = Depends(get_db)):
    db_dominio = db.query(Dominio).filter(Dominio.id == dominio_id).first()
    if not db_dominio:
        raise HTTPException(status_code=404, detail="Domínio não encontrado")
    
    for key, value in dominio.dict(exclude_unset=True).items():
        setattr(db_dominio, key, value)
    
    try:
        db.commit()
        db.refresh(db_dominio)
        return db_dominio
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Já existe outro registro com este nome de domínio.")

@router.delete("/{dominio_id}")
def delete_dominio(dominio_id: int, db: Session = Depends(get_db)):
    db_dominio = db.query(Dominio).filter(Dominio.id == dominio_id).first()
    if not db_dominio:
        raise HTTPException(status_code=404, detail="Domínio não encontrado")
    
    db.delete(db_dominio)
    db.commit()
    return {"message": "Domínio excluído com sucesso"}
