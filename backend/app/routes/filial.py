from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.filial import Filial
from app.database import get_db

router = APIRouter()

@router.get('/filiais/', response_model=list)
def listar_filiais(db: Session = Depends(get_db)):
    filiais = db.query(Filial).all()
    return [{"id": f.id, "unidade": f.unidade} for f in filiais]
