from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.database import get_db
from app.models.grupo_whatsapp import GrupoWhatsapp
from app.models.funcionario import Funcionario
from app.schemas.grupo_whatsapp import (
    GrupoWhatsapp as GrupoWhatsappSchema,
    GrupoWhatsappCreate,
    GrupoWhatsappUpdate,
    GrupoWhatsappWithFuncionarios
)

router = APIRouter(prefix="/grupos_whatsapp", tags=["grupos_whatsapp"])

@router.get("/", response_model=List[GrupoWhatsappWithFuncionarios])
def listar_grupos_whatsapp(db: Session = Depends(get_db)):
    """Lista todos os grupos de WhatsApp com seus funcionários"""
    grupos = db.query(GrupoWhatsapp).options(
        joinedload(GrupoWhatsapp.funcionarios)
    ).all()
    
    # Converter para o formato esperado
    resultado = []
    for grupo in grupos:
        funcionarios_dict = [
            {
                "id": f.id,
                "nome": f.nome,
                "sobrenome": f.sobrenome,
                "email": f.email
            }
            for f in grupo.funcionarios
        ]
        
        resultado.append({
            "id": grupo.id,
            "nome": grupo.nome,
            "descricao": grupo.descricao,
            "funcionarios": funcionarios_dict
        })
    
    return resultado

@router.get("/{grupo_id}", response_model=GrupoWhatsappWithFuncionarios)
def obter_grupo_whatsapp(grupo_id: int, db: Session = Depends(get_db)):
    """Obtém um grupo de WhatsApp específico com seus funcionários"""
    grupo = db.query(GrupoWhatsapp).options(
        joinedload(GrupoWhatsapp.funcionarios)
    ).filter(GrupoWhatsapp.id == grupo_id).first()
    
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo de WhatsApp não encontrado")
    
    # Converter funcionários para dict
    funcionarios_dict = [
        {
            "id": f.id,
            "nome": f.nome,
            "sobrenome": f.sobrenome,
            "email": f.email
        }
        for f in grupo.funcionarios
    ]
    
    return {
        "id": grupo.id,
        "nome": grupo.nome,
        "descricao": grupo.descricao,
        "funcionarios": funcionarios_dict
    }

@router.post("/", response_model=GrupoWhatsappSchema)
def criar_grupo_whatsapp(grupo: GrupoWhatsappCreate, db: Session = Depends(get_db)):
    """Cria um novo grupo de WhatsApp"""
    # Verificar se já existe um grupo com o mesmo nome
    grupo_existente = db.query(GrupoWhatsapp).filter(GrupoWhatsapp.nome == grupo.nome).first()
    if grupo_existente:
        raise HTTPException(status_code=400, detail="Já existe um grupo com este nome")
    
    db_grupo = GrupoWhatsapp(**grupo.dict())
    db.add(db_grupo)
    db.commit()
    db.refresh(db_grupo)
    return db_grupo

@router.put("/{grupo_id}", response_model=GrupoWhatsappSchema)
def atualizar_grupo_whatsapp(
    grupo_id: int, 
    grupo_update: GrupoWhatsappUpdate, 
    db: Session = Depends(get_db)
):
    """Atualiza um grupo de WhatsApp"""
    grupo = db.query(GrupoWhatsapp).filter(GrupoWhatsapp.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo de WhatsApp não encontrado")
    
    # Verificar se o novo nome já existe (se nome foi alterado)
    if grupo_update.nome and grupo_update.nome != grupo.nome:
        grupo_existente = db.query(GrupoWhatsapp).filter(GrupoWhatsapp.nome == grupo_update.nome).first()
        if grupo_existente:
            raise HTTPException(status_code=400, detail="Já existe um grupo com este nome")
    
    update_data = grupo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(grupo, field, value)
    
    db.commit()
    db.refresh(grupo)
    return grupo

@router.delete("/{grupo_id}")
def excluir_grupo_whatsapp(grupo_id: int, db: Session = Depends(get_db)):
    """Exclui um grupo de WhatsApp"""
    grupo = db.query(GrupoWhatsapp).filter(GrupoWhatsapp.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo de WhatsApp não encontrado")
    
    db.delete(grupo)
    db.commit()
    return {"detail": "Grupo de WhatsApp excluído com sucesso"}

@router.post("/{grupo_id}/funcionarios/{funcionario_id}")
def adicionar_funcionario_ao_grupo(
    grupo_id: int, 
    funcionario_id: int, 
    db: Session = Depends(get_db)
):
    """Adiciona um funcionário ao grupo de WhatsApp"""
    grupo = db.query(GrupoWhatsapp).filter(GrupoWhatsapp.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo de WhatsApp não encontrado")
    
    funcionario = db.query(Funcionario).filter(Funcionario.id == funcionario_id).first()
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    
    # Verificar se o funcionário já está no grupo
    if funcionario in grupo.funcionarios:
        raise HTTPException(status_code=400, detail="Funcionário já está no grupo")
    
    grupo.funcionarios.append(funcionario)
    db.commit()
    return {"detail": "Funcionário adicionado ao grupo com sucesso"}

@router.delete("/{grupo_id}/funcionarios/{funcionario_id}")
def remover_funcionario_do_grupo(
    grupo_id: int, 
    funcionario_id: int, 
    db: Session = Depends(get_db)
):
    """Remove um funcionário do grupo de WhatsApp"""
    grupo = db.query(GrupoWhatsapp).filter(GrupoWhatsapp.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo de WhatsApp não encontrado")
    
    funcionario = db.query(Funcionario).filter(Funcionario.id == funcionario_id).first()
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    
    # Verificar se o funcionário está no grupo
    if funcionario not in grupo.funcionarios:
        raise HTTPException(status_code=400, detail="Funcionário não está no grupo")
    
    grupo.funcionarios.remove(funcionario)
    db.commit()
    return {"detail": "Funcionário removido do grupo com sucesso"}
