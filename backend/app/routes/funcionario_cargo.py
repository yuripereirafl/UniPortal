from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.funcionario_cargo import FuncionarioCargo
from app.schemas.funcionario_cargo import FuncionarioCargoCreate, FuncionarioCargoRead

router = APIRouter()

@router.get("/funcionarios-cargos/", response_model=list[FuncionarioCargoRead])
def list_funcionarios_cargos(db: Session = Depends(get_db)):
    return db.query(FuncionarioCargo).all()

@router.post("/funcionarios-cargos/", response_model=FuncionarioCargoRead)
def create_funcionario_cargo(cargo: FuncionarioCargoCreate, db: Session = Depends(get_db)):
    db_cargo = FuncionarioCargo(**cargo.dict())
    db.add(db_cargo)
    db.commit()
    db.refresh(db_cargo)
    return db_cargo
