from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.notebook import Notebook
from app.schemas.notebook import NotebookCreate, NotebookUpdate, NotebookResponse

router = APIRouter()

@router.get("/", response_model=List[NotebookResponse])
def get_notebooks(db: Session = Depends(get_db)):
    return db.query(Notebook).all()

@router.post("/", response_model=NotebookResponse)
def create_notebook(notebook: NotebookCreate, db: Session = Depends(get_db)):
    db_notebook = Notebook(**notebook.dict())
    db.add(db_notebook)
    db.commit()
    db.refresh(db_notebook)
    return db_notebook

@router.put("/{notebook_id}", response_model=NotebookResponse)
def update_notebook(notebook_id: int, notebook: NotebookUpdate, db: Session = Depends(get_db)):
    db_notebook = db.query(Notebook).filter(Notebook.id == notebook_id).first()
    if not db_notebook:
        raise HTTPException(status_code=404, detail="Notebook não encontrado")
    
    for key, value in notebook.dict(exclude_unset=True).items():
        setattr(db_notebook, key, value)
    
    db.commit()
    db.refresh(db_notebook)
    return db_notebook

@router.delete("/{notebook_id}")
def delete_notebook(notebook_id: int, db: Session = Depends(get_db)):
    db_notebook = db.query(Notebook).filter(Notebook.id == notebook_id).first()
    if not db_notebook:
        raise HTTPException(status_code=404, detail="Notebook não encontrado")
    
    db.delete(db_notebook)
    db.commit()
    return {"message": "Notebook excluído com sucesso"}
