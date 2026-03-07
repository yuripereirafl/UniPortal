import pandas as pd
import os
import sys
from pathlib import Path
import re
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adicionar caminho do backend
backend_dir = Path(r"c:\Users\yuri.flores\Desktop\Projetos Sistemas\UniPortal-Portal_atual\backend")
sys.path.insert(0, str(backend_dir))

# Importar modelos DIRETAMENTE sem passar por database.py para evitar importações circulares problemáticas
from app.models.base import Base
from app.models.sistema import Sistema # Necessário se Funcionario usar
from app.models.setor import Setor
from app.models.funcionario import Funcionario, funcionario_setor, funcionario_sistema
from app.models.celular import CelularLinha, CelularConta

# Carregar config localmente
from dotenv import load_dotenv
load_dotenv()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "dadosrh")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dadosrh")
DB_NAME = os.getenv("DB_NAME", "dadosrh")
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clean_number(num):
    if not num or str(num) == 'nan': return None
    return re.sub(r'[^0-9]', '', str(num))

def run_import():
    file_path = r"c:\Users\yuri.flores\Desktop\Projetos Sistemas\UniPortal-Portal_atual\04 - PLANO_CELULARES_2025.xlsx"
    print("📖 Lendo sheet 'Conta Google'...")
    df = pd.read_excel(file_path, sheet_name='Conta Google', header=None)
    df_data = df.iloc[2:]

    db = SessionLocal()
    print("🚀 Iniciando migração...")
    stats = {"sucesso": 0, "contas": 0, "func": 0}
    
    try:
        for _, row in df_data.iterrows():
            imei = str(row[2]).strip() if pd.notna(row[2]) else None
            num_chip = str(row[8]).strip() if pd.notna(row[8]) else None
            nome_func = str(row[5]).strip() if pd.notna(row[5]) else None
            
            if (not imei or imei == 'X' or imei == 'nan') and (not num_chip or num_chip == 'nan'):
                continue

            # Tenta achar funcionário
            func = None
            if nome_func and nome_func != 'X':
                func = db.query(Funcionario).filter((Funcionario.nome + " " + Funcionario.sobrenome).ilike(f"%{nome_func}%")).first()
                if func: stats["func"] += 1

            # Setor
            setor_nome = str(row[6]).strip() if pd.notna(row[6]) else None
            setor = None
            if setor_nome and setor_nome != 'X':
                setor = db.query(Setor).filter(Setor.nome.ilike(f"%{setor_nome}%")).first()

            # Linha
            cel = db.query(CelularLinha).filter(CelularLinha.imei == imei).first() if imei and imei != 'X' else None
            if not cel:
                cel = CelularLinha(
                    marca=str(row[0]) if pd.notna(row[0]) else None,
                    modelo=str(row[1]) if pd.notna(row[1]) else None,
                    imei=imei if imei != 'X' else None,
                    numero_chip=num_chip if num_chip != 'nan' else None,
                    plano="CLARO",
                    funcionario_id=func.id if func else None,
                    setor_id=setor.id if setor else None,
                    whatsapp=str(row[11]) if pd.notna(row[11]) else None
                )
                db.add(cel)
            db.flush()

            # Conta
            gmail = str(row[3]).strip() if pd.notna(row[3]) else None
            if gmail and '@' in gmail:
                conta = db.query(CelularConta).filter(CelularConta.gmail == gmail).first()
                if not conta:
                    db.add(CelularConta(
                        gmail=gmail,
                        senha=str(row[4]) if pd.notna(row[4]) else None,
                        celular_id=cel.id,
                        funcionario_id=func.id if func else None
                    ))
                    stats["contas"] += 1
            
            stats["sucesso"] += 1
        
        db.commit()
        print(f"✅ Fim! {stats['sucesso']} processados, {stats['contas']} contas, {stats['func']} funcs vinculados.")
    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    import traceback
    run_import()
