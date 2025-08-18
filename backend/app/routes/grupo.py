from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.grupos import Grupo

router = APIRouter()

@router.get('/grupos/')
def listar_grupos(db: Session = Depends(get_db)):
    grupos = db.query(Grupo).all()
    return grupos