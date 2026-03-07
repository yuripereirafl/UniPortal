import pandas as pd
import os
import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(r"c:\Users\yuri.flores\Desktop\Projetos Sistemas\UniPortal-Portal_atual\backend")
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal, engine
from app.models.base import Base
# Importar todos os modelos para garantir que a metadata os conheça
from app.models.funcionario import Funcionario
from app.models.setor import Setor
from app.models.celular import CelularLinha, CelularConta

def run_import():
    file_path = r"c:\Users\yuri.flores\Desktop\Projetos Sistemas\UniPortal-Portal_atual\04 - PLANO_CELULARES_2025.xlsx"
    
    print("📖 Lendo planilha...")
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"❌ Erro ao ler planilha: {e}")
        return

    df.columns = [c.strip().upper() for c in df.columns]

    def clean(val):
        v = str(val).strip()
        if v.lower() in ('nan', 'none', 'x', ''): return None
        return v

    db = SessionLocal()
    print("🚀 Iniciando processamento...")
    try:
        success = 0
        total = len(df)
        for index, row in df.iterrows():
            # Buscar Funcionario e Setor
            func_nome = clean(row.get('FUNCIONARIO', ''))
            funcionario = None
            if func_nome:
                funcionario = db.query(Funcionario).filter(Funcionario.nome.ilike(f"%{func_nome}%")).first()
            
            setor_nome = clean(row.get('SETOR', ''))
            setor = None
            if setor_nome:
                setor = db.query(Setor).filter(Setor.nome.ilike(f"%{setor_nome}%")).first()

            nova_linha = CelularLinha(
                marca=clean(row.get('MARCA', '')),
                modelo=clean(row.get('MODELO', '')),
                imei=clean(row.get('IMEI', '')),
                numero_chip=clean(row.get('CHIP', '')),
                plano=clean(row.get('PLANO', '')),
                tipo_pagamento=clean(row.get('PRÉ OU PÓS PAGO', '')),
                whatsapp=clean(row.get('WHATSAPP P', '')),
                bloqueio=clean(row.get('BLOQUEIO CELULAR', '')),
                funcionario_id=funcionario.id if funcionario else None,
                setor_id=setor.id if setor else None
            )
            db.add(nova_linha)
            db.flush() 
            
            gmail = clean(row.get('GMAIL', ''))
            if gmail:
                nova_conta = CelularConta(
                    gmail=gmail,
                    senha=clean(row.get('SENHA ( @ ANTES)', row.get('SENHA', ''))),
                    celular_id=nova_linha.id,
                    funcionario_id=funcionario.id if funcionario else None
                )
                db.add(nova_conta)
            
            success += 1
            if success % 10 == 0:
                print(f"Processando: {success}/{total}...")
        
        db.commit()
        print(f"✅ Sucesso! {success} registros importados/processados.")
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_import()
