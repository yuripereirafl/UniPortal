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

print("="*80)
print("ANÁLISE: VENDAS POR FILIAL DOS 48 IDS DA EQUIPE DA BRUNA")
print("="*80)

with engine.connect() as conn:
    # 1. Buscar os 48 IDs (mesmo algoritmo do backend)
    # Nível 1
    result = conn.execute(text("""
        SELECT id_eyal, nome, cargo
        FROM rh_homologacao.metas_colaboradores
        WHERE lider_direto = 'BRUNA FURQUIM DIAS'
          AND mes_ref = '2025-10-01'
    """))
    nivel1 = [('4987', 'BRUNA FURQUIM DIAS', 'COORDENADOR(A)')]  # Líder
    nivel1.extend([(r[0], r[1], r[2]) for r in result.fetchall()])
    
    # Nível 2
    supervisores = [nome for id_, nome, cargo in nivel1 if 'supervisor' in cargo.lower() or 'monitor' in cargo.lower()]
    nivel2 = []
    if supervisores:
        placeholders = ','.join([f":sup{i}" for i in range(len(supervisores))])
        params = {f"sup{i}": sup for i, sup in enumerate(supervisores)}
        result = conn.execute(text(f"""
            SELECT id_eyal, nome, cargo
            FROM rh_homologacao.metas_colaboradores
            WHERE lider_direto IN ({placeholders})
              AND mes_ref = '2025-10-01'
        """), params)
        nivel2 = [(r[0], r[1], r[2]) for r in result.fetchall()]
    
    # ADM
    result = conn.execute(text("""
        SELECT id_eyal, nome, cargo
        FROM rh_homologacao.metas_colaboradores
        WHERE mes_ref = '2025-10-01'
          AND unidade = 'CENTRAL DE MARCACÕES'
          AND (equipe IS NULL OR equipe = '')
          AND nome != 'BRUNA FURQUIM DIAS'
    """))
    adm = [(r[0], r[1], r[2]) for r in result.fetchall()]
    
    todos_ids = list(set([id_ for id_, _, _ in nivel1 + nivel2 + adm]))
    
    print(f"\n📊 Total de IDs encontrados: {len(todos_ids)}")
    print(f"   - Nível 1 (líder + diretos): {len(nivel1)}")
    print(f"   - Nível 2 (equipes): {len(nivel2)}")
    print(f"   - ADM (sem equipe): {len(adm)}")
    
    # 2. Buscar vendas AGRUPADAS POR FILIAL para esses IDs
    placeholders = ','.join([f":id{i}" for i in range(len(todos_ids))])
    params = {f"id{i}": id_ for i, id_ in enumerate(todos_ids)}
    
    result = conn.execute(text(f"""
        SELECT 
            filial,
            COUNT(*) as qtd_vendas,
            COUNT(DISTINCT cod_usuario) as qtd_vendedores
        FROM rh_homologacao.basecampanhas
        WHERE cod_usuario IN ({placeholders})
          AND EXTRACT(year FROM mes) = 2025
          AND EXTRACT(month FROM mes) = 10
        GROUP BY filial
        ORDER BY qtd_vendas DESC
    """), params)
    
    print(f"\n🔍 VENDAS DOS 48 IDS AGRUPADAS POR FILIAL:")
    print(f"   {'Filial':<30} | Vendas | Vendedores")
    print(f"   {'-'*30}-|--------|------------")
    
    total_vendas = 0
    for filial, qtd_vendas, qtd_vendedores in result.fetchall():
        if filial:
            match = "✅" if filial == 'CENTRAL DE MARCACÕES' else "⚠️"
            print(f"   {match} {filial:<28} | {qtd_vendas:>6} | {qtd_vendedores:>10}")
            total_vendas += qtd_vendas
        else:
            print(f"   ❌ NULL{' '*25} | {qtd_vendas:>6} | {qtd_vendedores:>10}")
            total_vendas += qtd_vendas
    
    print(f"   {'-'*30}-|--------|------------")
    print(f"   TOTAL{' '*25} | {total_vendas:>6} |")
    
    # 3. Listar quais IDs vendem em filiais diferentes
    result = conn.execute(text(f"""
        SELECT 
            cod_usuario,
            filial,
            COUNT(*) as qtd
        FROM rh_homologacao.basecampanhas
        WHERE cod_usuario IN ({placeholders})
          AND EXTRACT(year FROM mes) = 2025
          AND EXTRACT(month FROM mes) = 10
          AND filial != 'CENTRAL DE MARCACÕES'
        GROUP BY cod_usuario, filial
        ORDER BY qtd DESC
    """), params)
    
    vendas_outras = result.fetchall()
    if vendas_outras:
        print(f"\n⚠️ COLABORADORES VENDENDO EM OUTRAS FILIAIS:")
        for cod_usuario, filial, qtd in vendas_outras:
            # Buscar nome
            nome_result = conn.execute(text("""
                SELECT nome
                FROM rh_homologacao.metas_colaboradores
                WHERE id_eyal = :id
                  AND mes_ref = '2025-10-01'
                LIMIT 1
            """), {"id": cod_usuario})
            nome = nome_result.fetchone()
            nome = nome[0] if nome else "DESCONHECIDO"
            print(f"   - {cod_usuario} ({nome}): {qtd} vendas em '{filial}'")

print("\n" + "="*80)
