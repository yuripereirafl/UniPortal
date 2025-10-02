from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.permissao import Permissao

router = APIRouter()

@router.get('/permissoes/')
def listar_permissoes(db: Session = Depends(get_db)):
    permissoes = db.query(Permissao).all()
    return [{"id": p.id, "codigo": p.codigo, "descricao": p.descricao} for p in permissoes]
