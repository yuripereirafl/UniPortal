"""
Teste simples de conexão com tabela orcamentos
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

# Montar DATABASE_URL
db_user = os.getenv("DATABASE_USER", "postgres")
db_password = os.getenv("DATABASE_PASSWORD", "")
db_host = os.getenv("DATABASE_HOST", "localhost")
db_port = os.getenv("DATABASE_PORT", "5432")
db_name = os.getenv("DATABASE_NAME", "UniPortal")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

print("Conectando ao banco de dados...")
engine = create_engine(DATABASE_URL)
conn = engine.connect()

print("\n✅ TESTANDO TABELA ORCAMENTOS")
print("=" * 80)

# Total de registros
result = conn.execute(text('SELECT COUNT(*) FROM rh_homologacao.orcamentos'))
total = result.scalar()
print(f"Total de orçamentos: {total:,}")

# Exemplo de registro
result = conn.execute(text('''
    SELECT 
        seq_orcamento,
        cod_usuario,
        colab_orcou,
        criado,
        confirmado,
        unidade_usuario
    FROM rh_homologacao.orcamentos
    LIMIT 1
'''))
row = result.fetchone()

if row:
    print(f"\nExemplo de registro:")
    print(f"  Seq: {row[0]}")
    print(f"  Cod Usuario: {row[1]}")
    print(f"  Colaborador: {row[2]}")
    print(f"  Criado: {row[3]}")
    print(f"  Confirmado: {row[4]}")
    print(f"  Unidade: {row[5]}")

# Top colaboradores
print(f"\nTop 5 colaboradores com mais orçamentos:")
result = conn.execute(text('''
    SELECT 
        cod_usuario,
        colab_orcou,
        COUNT(*) as total,
        SUM(CASE WHEN confirmado = 'S' THEN 1 ELSE 0 END) as confirmados
    FROM rh_homologacao.orcamentos
    WHERE cod_usuario IS NOT NULL
    GROUP BY cod_usuario, colab_orcou
    ORDER BY COUNT(*) DESC
    LIMIT 5
'''))

for i, (cod, nome, total, confirmados) in enumerate(result.fetchall(), 1):
    taxa = (confirmados / total * 100) if total > 0 else 0
    print(f"  {i}. {nome} (ID: {cod}) - {total} orçamentos ({confirmados} confirmados - {taxa:.1f}%)")

conn.close()

print("\n✅ API ENDPOINTS PRONTOS:")
print("  GET /orcamentos/colaborador/{cod_usuario}?mes_ref=YYYY-MM")
print("  GET /orcamentos/historico/{cod_usuario}?limite=12")
print("  GET /orcamentos/equipe/{nome_equipe}?mes_ref=YYYY-MM")
print("=" * 80)
