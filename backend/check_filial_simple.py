import sys
sys.stdout.reconfigure(encoding='utf-8')

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Criar engine direta
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "dadosrh")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dadosrh")
DB_NAME = os.getenv("DB_NAME", "dadosrh")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

print("="*70)
print("VERIFICAÇÃO: FILIAL vs UNIDADE")
print("="*70)

with engine.connect() as conn:
    # 1. Unidade da Bruna
    result = conn.execute(text("""
        SELECT unidade
        FROM rh_homologacao.metas_colaboradores
        WHERE id_eyal = '4987' AND mes_ref = '2025-10-01'
    """))
    unidade_bruna = result.fetchone()[0]
    
    print(f"\n1️⃣ Unidade da Bruna:")
    print(f"   Valor: '{unidade_bruna}'")
    print(f"   Tamanho: {len(unidade_bruna)} caracteres")
    print(f"   Repr: {repr(unidade_bruna)}")
    print(f"   Hex: {unidade_bruna.encode('utf-8').hex()}")
    
    # 2. Filiais distintas
    result = conn.execute(text("""
        SELECT filial, COUNT(*) as qtd
        FROM rh_homologacao.basecampanhas
        WHERE EXTRACT(year FROM mes) = 2025
          AND EXTRACT(month FROM mes) = 10
        GROUP BY filial
        ORDER BY qtd DESC
    """))
    
    print(f"\n2️⃣ Filiais DISTINTAS em basecampanhas (out/2025):")
    filiais = result.fetchall()
    for filial, qtd in filiais:
        if filial:
            print(f"   '{filial}' ({len(filial)} chars): {qtd} vendas")
            print(f"      Hex: {filial.encode('utf-8').hex()}")
        else:
            print(f"   NULL: {qtd} vendas")
    
    # 3. Match exato
    result = conn.execute(text("""
        SELECT COUNT(*)
        FROM rh_homologacao.basecampanhas
        WHERE filial = :unidade
          AND EXTRACT(year FROM mes) = 2025
          AND EXTRACT(month FROM mes) = 10
    """), {"unidade": unidade_bruna})
    vendas_exato = result.fetchone()[0]
    
    print(f"\n3️⃣ Vendas com filial = '{unidade_bruna}' (match exato): {vendas_exato}")
    
    # 4. Match com TRIM/UPPER
    result = conn.execute(text("""
        SELECT COUNT(*)
        FROM rh_homologacao.basecampanhas
        WHERE UPPER(TRIM(filial)) = UPPER(TRIM(:unidade))
          AND EXTRACT(year FROM mes) = 2025
          AND EXTRACT(month FROM mes) = 10
    """), {"unidade": unidade_bruna})
    vendas_trim = result.fetchone()[0]
    
    print(f"4️⃣ Vendas com filial (TRIM/UPPER): {vendas_trim}")
    
    # 5. Vendas com filial LIKE
    result = conn.execute(text("""
        SELECT filial, COUNT(*) as qtd
        FROM rh_homologacao.basecampanhas
        WHERE UPPER(filial) LIKE '%CENTRAL%'
          AND EXTRACT(year FROM mes) = 2025
          AND EXTRACT(month FROM mes) = 10
        GROUP BY filial
    """))
    
    print(f"\n5️⃣ Filiais com 'CENTRAL' no nome:")
    for filial, qtd in result.fetchall():
        match = "✅ MATCH!" if filial == unidade_bruna else "❌"
        print(f"   {match} '{filial}': {qtd} vendas")

print("\n" + "="*70)
