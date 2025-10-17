import sys
sys.stdout.reconfigure(encoding='utf-8')

from app.database import SessionLocal
from app.models.metas_colaboradores import MetaColaborador
from app.models.vendas import BaseCampanhas
from sqlalchemy import extract, func, distinct
from datetime import date

db = SessionLocal()

# 1. Unidade da Bruna
bruna = db.query(MetaColaborador).filter(
    MetaColaborador.id_eyal == '4987',
    MetaColaborador.mes_ref == date(2025, 10, 1)
).first()

print("="*70)
print("VERIFICAÇÃO: FILIAL vs UNIDADE")
print("="*70)
print(f"\n1️⃣ Unidade da Bruna em metas_colaboradores:")
print(f"   Valor: '{bruna.unidade}'")
print(f"   Tamanho: {len(bruna.unidade)} caracteres")
print(f"   Repr: {repr(bruna.unidade)}")

# 2. Valores distintos de filial
filiais_query = db.query(
    BaseCampanhas.filial,
    func.count().label('qtd')
).filter(
    extract('year', BaseCampanhas.mes) == 2025,
    extract('month', BaseCampanhas.mes) == 10
).group_by(BaseCampanhas.filial).order_by(func.count().desc()).all()

print(f"\n2️⃣ Valores DISTINTOS de 'filial' em basecampanhas (out/2025):")
for filial, qtd in filiais_query:
    if filial:
        print(f"   '{filial}' ({len(filial)} chars): {qtd} vendas | Repr: {repr(filial)}")
    else:
        print(f"   NULL: {qtd} vendas")

# 3. Buscar vendas com filial = unidade_bruna (exato)
vendas_exato = db.query(func.count(BaseCampanhas.cod_usuario)).filter(
    BaseCampanhas.filial == bruna.unidade,
    extract('year', BaseCampanhas.mes) == 2025,
    extract('month', BaseCampanhas.mes) == 10
).scalar()

print(f"\n3️⃣ Vendas com filial = '{bruna.unidade}' (match exato): {vendas_exato}")

# 4. Buscar vendas com filial TRIM/UPPER
vendas_trim = db.query(func.count(BaseCampanhas.cod_usuario)).filter(
    func.upper(func.trim(BaseCampanhas.filial)) == func.upper(func.trim(bruna.unidade)),
    extract('year', BaseCampanhas.mes) == 2025,
    extract('month', BaseCampanhas.mes) == 10
).scalar()

print(f"4️⃣ Vendas com filial (TRIM/UPPER): {vendas_trim}")

# 5. Buscar vendas por IDs (método antigo)

# Buscar todos IDs da equipe (simulando lógica do backend)
ids_nivel1 = [bruna.id_eyal]
liderados_n1 = db.query(MetaColaborador).filter(
    MetaColaborador.lider_direto == bruna.nome,
    MetaColaborador.mes_ref == date(2025, 10, 1)
).all()

for liderado in liderados_n1:
    ids_nivel1.append(liderado.id_eyal)

# Nível 2
supervisores = [l.nome for l in liderados_n1 if 'supervisor' in l.cargo.lower() or 'monitor' in l.cargo.lower()]
ids_nivel2 = []
if supervisores:
    liderados_n2 = db.query(MetaColaborador).filter(
        MetaColaborador.lider_direto.in_(supervisores),
        MetaColaborador.mes_ref == date(2025, 10, 1)
    ).all()
    ids_nivel2 = [l.id_eyal for l in liderados_n2]

# ADM
adm_query = db.query(MetaColaborador).filter(
    MetaColaborador.mes_ref == date(2025, 10, 1),
    MetaColaborador.unidade == bruna.unidade,
    (MetaColaborador.equipe.is_(None)) | (MetaColaborador.equipe == ''),
    MetaColaborador.nome != bruna.nome
).all()
ids_adm = [a.id_eyal for a in adm_query]

todos_ids = list(set(ids_nivel1 + ids_nivel2 + ids_adm))

vendas_ids = db.query(func.count(BaseCampanhas.cod_usuario)).filter(
    BaseCampanhas.cod_usuario.in_(todos_ids),
    extract('year', BaseCampanhas.mes) == 2025,
    extract('month', BaseCampanhas.mes) == 10
).scalar()

print(f"5️⃣ Vendas usando IDs ({len(todos_ids)} IDs): {vendas_ids}")

# 6. Comparação entre filiais e unidade
print(f"\n6️⃣ COMPARAÇÃO:")
print(f"   Unidade Bruna: '{bruna.unidade}'")
for filial, qtd in filiais_query[:5]:  # Top 5
    if filial:
        match = "✅ MATCH!" if filial == bruna.unidade else "❌"
        print(f"   {match} Filial: '{filial}' ({qtd} vendas)")

db.close()

print("\n" + "="*70)
