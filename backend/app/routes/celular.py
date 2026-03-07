from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io

from ..database import get_db
from ..models.celular import CelularLinha, CelularConta
from ..models.funcionario import Funcionario
from ..models.setor import Setor
from ..schemas.celular import (
    CelularLinha as CelularLinhaSchema, CelularLinhaCreate, CelularLinhaUpdate,
    CelularConta as CelularContaSchema, CelularContaCreate, CelularContaUpdate
)

router = APIRouter(prefix="/celulares", tags=["Celulares"])

# --- LINHAS ---

@router.get("/linhas", response_model=List[CelularLinhaSchema])
def list_linhas(db: Session = Depends(get_db)):
    return db.query(CelularLinha).all()

@router.post("/linhas", response_model=CelularLinhaSchema)
def create_linha(linha: CelularLinhaCreate, db: Session = Depends(get_db)):
    db_linha = CelularLinha(**linha.model_dump())
    db.add(db_linha)
    db.commit()
    db.refresh(db_linha)
    return db_linha

@router.put("/linhas/{id}", response_model=CelularLinhaSchema)
def update_linha(id: int, linha: CelularLinhaUpdate, db: Session = Depends(get_db)):
    db_linha = db.query(CelularLinha).filter(CelularLinha.id == id).first()
    if not db_linha:
        raise HTTPException(status_code=404, detail="Linha não encontrada")
    
    update_data = linha.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_linha, key, value)
    
    db.commit()
    db.refresh(db_linha)
    return db_linha

@router.delete("/linhas/{id}")
def delete_linha(id: int, db: Session = Depends(get_db)):
    db_linha = db.query(CelularLinha).filter(CelularLinha.id == id).first()
    if not db_linha:
        raise HTTPException(status_code=404, detail="Linha não encontrada")
    db.delete(db_linha)
    db.commit()
    return {"message": "Linha removida com sucesso"}

# --- CONTAS ---

@router.get("/contas", response_model=List[CelularContaSchema])
def list_contas(db: Session = Depends(get_db)):
    return db.query(CelularConta).all()

@router.post("/contas", response_model=CelularContaSchema)
def create_conta(conta: CelularContaCreate, db: Session = Depends(get_db)):
    db_conta = CelularConta(**conta.model_dump())
    db.add(db_conta)
    db.commit()
    db.refresh(db_conta)
    return db_conta

@router.put("/contas/{id}", response_model=CelularContaSchema)
def update_conta(id: int, conta: CelularContaUpdate, db: Session = Depends(get_db)):
    db_conta = db.query(CelularConta).filter(CelularConta.id == id).first()
    if not db_conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    
    update_data = conta.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_conta, key, value)
    
    db.commit()
    db.refresh(db_conta)
    return db_conta

@router.delete("/contas/{id}")
def delete_conta(id: int, db: Session = Depends(get_db)):
    db_conta = db.query(CelularConta).filter(CelularConta.id == id).first()
    if not db_conta:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    db.delete(db_conta)
    db.commit()
    return {"message": "Conta removida com sucesso"}

# --- IMPORTAR ---

@router.post("/importar")
async def importar_celulares(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            # Tenta ler a aba correta se for a planilha padrão, caso contrário lê a primeira
            try:
                df = pd.read_excel(io.BytesIO(content), sheet_name='Conta Google', header=1)
            except Exception:
                df = pd.read_excel(io.BytesIO(content))
        
        # Normalizar nomes das colunas (remover espaços e colocar tudo em maiúscula)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        def clean(val):
            if pd.isna(val): return None
            v = str(val).strip()
            if v.lower() in ('nan', 'none', 'x', ''): return None
            if v.endswith('.0'): return v[:-2]
            return v

        registros_importados = 0
        erros = []
        
        for index, row in df.iterrows():
            try:
                imei = clean(row.get('IMEI', ''))
                numero_chip = clean(row.get('CHIP', ''))
                
                # Se não tem IMEI e não tem CHIP, pula a linha vazia/inválida
                if not imei and not numero_chip:
                    continue

                # 1. Buscar Funcionario
                func_nome = clean(row.get('FUNCIONARIO', ''))
                funcionario = None
                if func_nome:
                    funcionario = db.query(Funcionario).filter((Funcionario.nome + " " + Funcionario.sobrenome).ilike(f"%{func_nome}%")).first()
                
                # 2. Buscar Setor
                setor_nome = clean(row.get('SETOR', ''))
                setor = None
                if setor_nome:
                    setor = db.query(Setor).filter(Setor.nome.ilike(f"%{setor_nome}%")).first()

                # 3. Criar ou Atualizar Linha
                nova_linha = None
                if imei:
                    nova_linha = db.query(CelularLinha).filter(CelularLinha.imei == imei).first()
                
                if not nova_linha:
                    nova_linha = CelularLinha(
                        marca=clean(row.get('MARCA', '')),
                        modelo=clean(row.get('MODELO', '')),
                        imei=imei,
                        numero_chip=numero_chip,
                        plano=clean(row.get('PLANO', 'CLARO')),
                        tipo_pagamento=clean(row.get('PRÉ OU PÓS PAGO', '')),
                        whatsapp=clean(row.get('WHATSAPP PIN', row.get('WHATSAPP P', ''))),
                        bloqueio=clean(row.get('BLOQUEIO CELULAR', '')),
                        funcionario_id=funcionario.id if funcionario else None,
                        setor_id=setor.id if setor else None
                    )
                    db.add(nova_linha)
                else:
                    # Atualiza os dados da linha existente
                    if funcionario: nova_linha.funcionario_id = funcionario.id
                    if setor: nova_linha.setor_id = setor.id
                    if numero_chip: nova_linha.numero_chip = numero_chip

                db.flush() # Para garantir que tem ID pra criar a conta
                
                # 4. Criar Conta Google associada
                gmail = clean(row.get('GMAIL', ''))
                if gmail and '@' in gmail:
                    conta_existente = db.query(CelularConta).filter(CelularConta.gmail == gmail).first()
                    if not conta_existente:
                        nova_conta = CelularConta(
                            gmail=gmail,
                            senha=clean(row.get('SENHA ( @ ANTES)', row.get('SENHA', ''))),
                            celular_id=nova_linha.id,
                            funcionario_id=funcionario.id if funcionario else None
                        )
                        db.add(nova_conta)
                
                registros_importados += 1
                
            except Exception as e:
                erros.append(f"Erro na linha {index + 2}: {str(e)}")
        
        db.commit()
        return {
            "status": "success",
            "imported": registros_importados,
            "errors": erros
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
