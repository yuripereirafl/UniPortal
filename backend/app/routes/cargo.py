from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.cargo import Cargo
from app.schemas.cargo import CargoCreate, CargoOut
from app.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/cargos/', response_model=list[CargoOut])
def listar_cargos(db: Session = Depends(get_db)):
    return db.query(Cargo).all()

@router.post('/cargos/', response_model=CargoOut)
def criar_cargo(cargo: CargoCreate, db: Session = Depends(get_db)):
    db_cargo = Cargo(**cargo.dict())
    db.add(db_cargo)
    db.commit()
    db.refresh(db_cargo)
    return db_cargo
