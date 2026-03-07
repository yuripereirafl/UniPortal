import os
import sys
from pathlib import Path
import re
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

backend_dir = Path(r"c:\Users\yuri.flores\Desktop\Projetos Sistemas\UniPortal-Portal_atual\backend")
sys.path.insert(0, str(backend_dir))

from app.models.base import Base
from app.models.sistema import Sistema
from app.models.setor import Setor
from app.models.funcionario import Funcionario, funcionario_setor, funcionario_sistema
from app.models.celular import CelularLinha, CelularConta

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

def clean(val):
    if pd.isna(val): return None
    v = str(val).strip()
    if v.lower() in ('nan', 'none', 'x', ''): return None
    return v

def run_clean_and_import():
    db = SessionLocal()
    try:
        # 1. Limpar tabelas
        print("🗑️ Limpando tabelas celulares_contas e celulares_linhas...")
        db.execute(text("DELETE FROM rh_homologacao.celulares_contas"))
        db.execute(text("DELETE FROM rh_homologacao.celulares_linhas"))
        db.commit()
        
        # 2. Ler os dados
        file_path = r"c:\Users\yuri.flores\Desktop\Projetos Sistemas\UniPortal-Portal_atual\04 - PLANO_CELULARES_2025.xlsx"
        print(f"📖 Lendo arquivo: {file_path}")
        df = pd.read_excel(file_path, sheet_name='Conta Google', header=1)
        df.columns = [str(c).strip().upper() for c in df.columns]

        print("🚀 Importando registros...")
        registros_importados = 0
        erros = []

        for index, row in df.iterrows():
            try:
                imei = clean(row.get('IMEI', ''))
                numero_chip = clean(row.get('CHIP', ''))
                
                # Pula linhas inúteis
                if not imei and not numero_chip:
                    continue

                # Buscar Funcionario
                func_nome = clean(row.get('FUNCIONARIO', ''))
                funcionario = None
                if func_nome:
                    funcionario = db.query(Funcionario).filter((Funcionario.nome + " " + Funcionario.sobrenome).ilike(f"%{func_nome}%")).first()
                
                # Buscar Setor
                setor_nome = clean(row.get('SETOR', ''))
                setor = None
                if setor_nome:
                    setor = db.query(Setor).filter(Setor.nome.ilike(f"%{setor_nome}%")).first()

                # Verificar se o IMEI já existe no banco ou se criamos agora
                nova_linha = None
                if imei:
                    nova_linha = db.query(CelularLinha).filter(CelularLinha.imei == imei).first()

                if not nova_linha:
                    # Criar Nova Linha
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
                    # Se já existe, apenas atualiza funcionário ou número se vazio 
                    if funcionario and not nova_linha.funcionario_id:
                        nova_linha.funcionario_id = funcionario.id
                    if numero_chip and not nova_linha.numero_chip:
                        nova_linha.numero_chip = numero_chip

                db.flush() # obtem ou sincroniza o id
                
                # Criar Conta Google
                gmail = clean(row.get('GMAIL', ''))
                if gmail and '@' in gmail:
                    nova_conta = CelularConta(
                        gmail=gmail,
                        senha=clean(row.get('SENHA ( @ ANTES)', row.get('SENHA', ''))),
                        celular_id=nova_linha.id,
                        funcionario_id=funcionario.id if funcionario else None
                    )
                    db.add(nova_conta)
                
                registros_importados += 1

            except Exception as e:
                erros.append(f"Erro index {index}: {e}")
                
        db.commit()
        print(f"✅ Sucesso! Foram importadas {registros_importados} linhas válidas e suas contas.")
        if erros:
            print("⚠️ Erros encontrados:")
            for err in erros: print("  -", err)
            
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        print(f"❌ Falha geral: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_clean_and_import()
