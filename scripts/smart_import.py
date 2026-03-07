import pandas as pd
import os
import sys
from pathlib import Path
import re

backend_dir = Path(r"c:\Users\yuri.flores\Desktop\Projetos Sistemas\UniPortal-Portal_atual\backend")
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.models.celular import CelularLinha, CelularConta
from app.models.funcionario import Funcionario
from app.models.setor import Setor

def clean_number(num):
    if not num or str(num) == 'nan': return None
    return re.sub(r'[^0-9]', '', str(num))

def run_import():
    file_path = r"c:\Users\yuri.flores\Desktop\Projetos Sistemas\UniPortal-Portal_atual\04 - PLANO_CELULARES_2025.xlsx"
    
    # 1. Carregar Planilha de Números (Nomes)
    print("📖 Lendo sheet 'CENTRAL - NÚMEROS'...")
    df_numbers = pd.read_excel(file_path, sheet_name='CENTRAL - NÚMEROS', header=None)
    # Filtra onde Coluna 2 (Número) tem dígitos
    df_numbers = df_numbers[df_numbers[2].astype(str).str.contains(r'\d', na=False)]
    
    # Map (Cleaned Number) -> Name
    number_to_name = {}
    for _, row in df_numbers.iterrows():
        name = str(row[1]).strip()
        num = clean_number(row[2])
        if num and name:
            number_to_name[num] = name

    # 2. Carregar Planilha de Contas (Celulares/IMEIs/Emails)
    print("📖 Lendo sheet 'Conta Google'...")
    df_accounts = pd.read_excel(file_path, sheet_name='Conta Google', header=None)
    
    # Inicia no index 4 (onde detectamos dados)
    df_accounts = df_accounts.iloc[4:]

    db = SessionLocal()
    print("🚀 Iniciando migração...")
    try:
        count = 0
        for _, row in df_accounts.iterrows():
            modelo = str(row[1]).strip()
            imei = str(row[2]).strip()
            gmail = str(row[3]).strip()
            num_raw = str(row[4]).strip()
            num_clean = clean_number(num_raw)
            senha = str(row[11]).strip()

            if not imei or imei == 'nan' or len(imei) < 5: continue

            # Tenta achar o nome se tiver o número
            funcionario = None
            if num_clean and num_clean in number_to_name:
                nome_func = number_to_name[num_clean]
                funcionario = db.query(Funcionario).filter(Funcionario.nome.ilike(f"%{nome_func}%")).first()

            # Criar Linha
            nova_linha = CelularLinha(
                marca=str(row[0]).strip() if str(row[0]) != 'nan' else 'MOTO',
                modelo=modelo,
                imei=imei,
                numero_chip=num_raw if num_raw != 'nan' else None,
                plano='CLARO',
                funcionario_id=funcionario.id if funcionario else None
            )
            db.add(nova_linha)
            db.flush()

            # Criar Conta
            if gmail and gmail != 'nan' and '@' in gmail:
                nova_conta = CelularConta(
                    gmail=gmail,
                    senha=senha if senha != 'nan' else None,
                    celular_id=nova_linha.id,
                    funcionario_id=funcionario.id if funcionario else None
                )
                db.add(nova_conta)
            
            count += 1

        db.commit()
        print(f"✅ Sucesso! {count} celulares e contas importados.")
        
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_import()
