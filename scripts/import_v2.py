import pandas as pd
import os
import sys
from pathlib import Path
import re
from datetime import datetime

# Adicionar caminho do backend
backend_dir = Path(r"c:\Users\yuri.flores\Desktop\Projetos Sistemas\UniPortal-Portal_atual\backend")
sys.path.insert(0, str(backend_dir))

# Tenta carregar todos os modelos para evitar erros de relacionamento do SQLAlchemy
from app.models.sistema import Sistema
from app.models.setor import Setor
from app.models.cargo import Cargo
from app.models.filial import Filial
from app.models.usuario import Usuario
from app.models.funcionario import Funcionario, funcionario_setor, funcionario_sistema
from app.models.celular import CelularLinha, CelularConta
from app.models.grupo_email import GrupoEmail
from app.models.grupo_whatsapp import GrupoWhatsapp
from app.models.grupo_pasta import GrupoPasta
from app.database import SessionLocal

def clean_number(num):
    if not num or str(num) == 'nan': return None
    return re.sub(r'[^0-9]', '', str(num))

def run_import():
    file_path = r"c:\Users\yuri.flores\Desktop\Projetos Sistemas\UniPortal-Portal_atual\04 - PLANO_CELULARES_2025.xlsx"
    
    print("📖 Lendo sheet 'Conta Google'...")
    # Lemos a partir da linha 2 (índice 2) onde começam os dados
    df = pd.read_excel(file_path, sheet_name='Conta Google', header=None)
    
    # Pulamos os headers (linhas 0 e 1)
    df_data = df.iloc[2:]

    db = SessionLocal()
    print("🚀 Iniciando migração de celulares e contas...")
    
    stats = {"pulo": 0, "sucesso": 0, "contas": 0, "funcionario_encontrado": 0}
    
    try:
        for index, row in df_data.iterrows():
            marca = str(row[0]).strip() if pd.notna(row[0]) else None
            modelo = str(row[1]).strip() if pd.notna(row[1]) else None
            imei = str(row[2]).strip() if pd.notna(row[2]) else None
            gmail = str(row[3]).strip() if pd.notna(row[3]) else None
            senha = str(row[4]).strip() if pd.notna(row[4]) else None
            nome_func_raw = str(row[5]).strip() if pd.notna(row[5]) else None
            setor_nome = str(row[6]).strip() if pd.notna(row[6]) else None
            plano = str(row[7]).strip() if pd.notna(row[7]) else None
            numero_chip = str(row[8]).strip() if pd.notna(row[8]) else None
            bloqueio = str(row[9]).strip() if pd.notna(row[9]) else None
            tipo_pagamento = str(row[10]).strip() if pd.notna(row[10]) else None
            whatsapp_pin = str(row[11]).strip() if pd.notna(row[11]) else None

            # Se não tem IMEI e não tem Número, provavelmente não é um registro útil
            if (not imei or imei == 'X' or imei == 'nan') and (not numero_chip or numero_chip == 'nan'):
                stats["pulo"] += 1
                continue

            # Buscar Funcionário
            funcionario = None
            if nome_func_raw and nome_func_raw != 'X':
                # Tenta match por nome completo ou partes
                parts = nome_func_raw.split(' ')
                if len(parts) >= 2:
                    nome = parts[0]
                    sobrenome = ' '.join(parts[1:])
                    funcionario = db.query(Funcionario).filter(
                        Funcionario.nome.ilike(f"%{nome}%"),
                        Funcionario.sobrenome.ilike(f"%{sobrenome}%")
                    ).first()
                
                if not funcionario:
                    # Tenta apenas pelo primeiro nome (menos preciso, mas ajuda se tiver abreviado)
                    funcionario = db.query(Funcionario).filter(Funcionario.nome.ilike(f"%{nome_func_raw}%")).first()
                
                if not funcionario:
                    # Tenta ilike no nome completo concatenado
                    funcionario = db.query(Funcionario).filter((Funcionario.nome + " " + Funcionario.sobrenome).ilike(f"%{nome_func_raw}%")).first()

            if funcionario:
                stats["funcionario_encontrado"] += 1

            # Buscar Setor
            setor = None
            if setor_nome and setor_nome != 'X':
                setor = db.query(Setor).filter(Setor.nome.ilike(f"%{setor_nome}%")).first()

            # Criar ou Atualizar CelularLinha
            # Usamos IMEI como chave única se disponível
            nova_linha = None
            if imei and imei != 'X' and imei != 'nan':
                nova_linha = db.query(CelularLinha).filter(CelularLinha.imei == imei).first()
            
            if not nova_linha:
                nova_linha = CelularLinha(
                    marca=marca if marca != 'X' else None,
                    modelo=modelo if modelo != 'X' else None,
                    imei=imei if imei != 'X' else None,
                    numero_chip=numero_chip if numero_chip != 'nan' else None,
                    plano=plano if pd.notna(row[7]) and not isinstance(row[7], (int, float, datetime)) else "CLARO",
                    tipo_pagamento=tipo_pagamento if tipo_pagamento != 'nan' else None,
                    whatsapp=whatsapp_pin if whatsapp_pin != 'nan' else None,
                    bloqueio=bloqueio if bloqueio != 'nan' else None,
                    funcionario_id=funcionario.id if funcionario else None,
                    setor_id=setor.id if setor else None
                )
                db.add(nova_linha)
            else:
                # Atualiza campos se já existir
                if funcionario: nova_linha.funcionario_id = funcionario.id
                if setor: nova_linha.setor_id = setor.id
                if numero_chip: nova_linha.numero_chip = numero_chip

            db.flush() # Para pegar o ID da nova_linha

            # Criar Conta se tiver Gmail
            if gmail and '@' in gmail:
                # Verifica se a conta já existe
                conta_existente = db.query(CelularConta).filter(CelularConta.gmail == gmail).first()
                if not conta_existente:
                    nova_conta = CelularConta(
                        gmail=gmail,
                        senha=senha if senha != 'nan' and senha != 'X' else None,
                        celular_id=nova_linha.id,
                        funcionario_id=funcionario.id if funcionario else None
                    )
                    db.add(nova_conta)
                    stats["contas"] += 1

            stats["sucesso"] += 1

            if stats["sucesso"] % 10 == 0:
                print(f"⏳ Processados: {stats['sucesso']}...")

        db.commit()
        print(f"\n✅ Migração concluída!")
        print(f"📊 Resumo:")
        print(f"   - Celulares processados: {stats['sucesso']}")
        print(f"   - Contas Google criadas: {stats['contas']}")
        print(f"   - Funcionários vinculados: {stats['funcionario_encontrado']}")
        print(f"   - Linhas ignoradas (sem dados): {stats['pulo']}")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro na migração: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_import()
