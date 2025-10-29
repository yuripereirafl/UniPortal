"""
Script para verificar a situação atual de meses nas tabelas de meta e realizado
"""

import os
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker
from app.models.metas_colaboradores import MetaColaborador
from app.models.realizado_colaboradores import RealizadoColaborador

# Configurar conexão
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "dadosrh")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dadosrh")
DB_NAME = os.getenv("DB_NAME", "dadosrh")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(
    DATABASE_URL,
    connect_args={"options": "-csearch_path=rh_homologacao,rh,public"}
)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print("\n" + "="*80)
print("VERIFICAÇÃO: MESES DISPONÍVEIS NAS TABELAS")
print("="*80 + "\n")

# 1. Verificar meses na tabela de metas
print("1. MESES DISPONÍVEIS NA TABELA metas_colaboradores:")
print("-" * 80)

try:
    meses_metas = db.query(
        distinct(MetaColaborador.mes_ref)
    ).order_by(MetaColaborador.mes_ref.desc()).all()
    
    if meses_metas:
        print(f"   Total de meses distintos: {len(meses_metas)}\n")
        for mes_row in meses_metas:
            mes = mes_row[0]
            qtd_colaboradores = db.query(MetaColaborador).filter(
                MetaColaborador.mes_ref == mes
            ).count()
            print(f"   📅 {mes} → {qtd_colaboradores} colaboradores com meta")
    else:
        print("   ❌ Nenhum mês encontrado na tabela metas_colaboradores")
except Exception as e:
    print(f"   ❌ Erro ao buscar meses: {e}")

print("\n" + "-" * 80 + "\n")

# 2. Verificar meses na tabela de realizado
print("2. MESES DISPONÍVEIS NA TABELA realizado_colaborador:")
print("-" * 80)

try:
    meses_realizado = db.query(
        distinct(RealizadoColaborador.mes_ref)
    ).order_by(RealizadoColaborador.mes_ref.desc()).all()
    
    if meses_realizado:
        print(f"   Total de meses distintos: {len(meses_realizado)}\n")
        for mes_row in meses_realizado:
            mes = mes_row[0]
            qtd_registros = db.query(RealizadoColaborador).filter(
                RealizadoColaborador.mes_ref == mes
            ).count()
            qtd_colaboradores = db.query(
                distinct(RealizadoColaborador.id_eyal)
            ).filter(
                RealizadoColaborador.mes_ref == mes
            ).count()
            print(f"   📅 {mes} → {qtd_registros} registros ({qtd_colaboradores} colaboradores)")
    else:
        print("   ❌ Nenhum mês encontrado na tabela realizado_colaborador")
except Exception as e:
    print(f"   ❌ Erro ao buscar meses: {e}")

print("\n" + "-" * 80 + "\n")

# 3. Verificar se há colaboradores com múltiplos meses
print("3. COLABORADORES COM METAS EM MÚLTIPLOS MESES:")
print("-" * 80)

try:
    # Buscar colaboradores que têm mais de 1 mês de meta
    colaboradores_multiplos = db.query(
        MetaColaborador.cpf,
        MetaColaborador.nome,
        func.count(distinct(MetaColaborador.mes_ref)).label('qtd_meses')
    ).group_by(
        MetaColaborador.cpf,
        MetaColaborador.nome
    ).having(
        func.count(distinct(MetaColaborador.mes_ref)) > 1
    ).order_by(
        func.count(distinct(MetaColaborador.mes_ref)).desc()
    ).limit(10).all()
    
    if colaboradores_multiplos:
        print(f"   Total de colaboradores com múltiplos meses: {len(colaboradores_multiplos)}\n")
        print(f"   {'CPF':<15} | {'Nome':<40} | {'Qtd Meses':>10}")
        print(f"   {'-'*15}|{'-'*42}|{'-'*12}")
        
        for cpf, nome, qtd_meses in colaboradores_multiplos[:10]:
            print(f"   {cpf:<15} | {nome:<40} | {qtd_meses:>10}")
            
            # Mostrar os meses deste colaborador
            meses_colab = db.query(
                MetaColaborador.mes_ref,
                MetaColaborador.meta_final
            ).filter(
                MetaColaborador.cpf == cpf
            ).order_by(MetaColaborador.mes_ref.desc()).all()
            
            for mes, meta in meses_colab:
                print(f"      → {mes}: R$ {meta:,.2f}")
            print()
    else:
        print("   ℹ️  Nenhum colaborador com múltiplos meses encontrado")
        print("   (Cada colaborador tem meta apenas para 1 mês)")
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "-" * 80 + "\n")

# 4. Verificar inconsistências (realizado sem meta, meta sem realizado)
print("4. VERIFICAÇÃO DE INCONSISTÊNCIAS:")
print("-" * 80)

try:
    # Pegar o último mês de meta
    ultimo_mes_meta = db.query(
        func.max(MetaColaborador.mes_ref)
    ).scalar()
    
    # Pegar o último mês de realizado
    ultimo_mes_realizado = db.query(
        func.max(RealizadoColaborador.mes_ref)
    ).scalar()
    
    print(f"   Último mês com META cadastrada: {ultimo_mes_meta}")
    print(f"   Último mês com REALIZADO cadastrado: {ultimo_mes_realizado}")
    
    if ultimo_mes_meta != ultimo_mes_realizado:
        print(f"\n   ⚠️  ATENÇÃO: Meses diferentes!")
        print(f"   Pode indicar que dados não estão sincronizados")
    else:
        print(f"\n   ✅ Último mês é o mesmo em ambas as tabelas")
    
    # Verificar colaboradores com realizado mas sem meta no último mês
    if ultimo_mes_realizado:
        ids_com_realizado = db.query(
            distinct(RealizadoColaborador.id_eyal)
        ).filter(
            RealizadoColaborador.mes_ref == ultimo_mes_realizado
        ).all()
        
        ids_com_realizado = [str(id[0]) for id in ids_com_realizado]
        
        ids_com_meta = db.query(
            distinct(MetaColaborador.id_eyal)
        ).filter(
            MetaColaborador.mes_ref == ultimo_mes_realizado
        ).all()
        
        ids_com_meta = [id[0] for id in ids_com_meta if id[0]]
        
        realizado_sem_meta = set(ids_com_realizado) - set(ids_com_meta)
        meta_sem_realizado = set(ids_com_meta) - set(ids_com_realizado)
        
        print(f"\n   Colaboradores com REALIZADO mas SEM META em {ultimo_mes_realizado}: {len(realizado_sem_meta)}")
        if realizado_sem_meta and len(realizado_sem_meta) <= 5:
            print(f"   IDs: {list(realizado_sem_meta)}")
        
        print(f"   Colaboradores com META mas SEM REALIZADO em {ultimo_mes_realizado}: {len(meta_sem_realizado)}")
        if meta_sem_realizado and len(meta_sem_realizado) <= 5:
            print(f"   IDs: {list(meta_sem_realizado)[:5]}")

except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "="*80 + "\n")

# 5. Exemplo prático: buscar um colaborador específico
print("5. EXEMPLO PRÁTICO - Colaborador ID 17035:")
print("-" * 80)

try:
    # Buscar metas deste colaborador
    metas = db.query(
        MetaColaborador.mes_ref,
        MetaColaborador.meta_final,
        MetaColaborador.nome
    ).filter(
        MetaColaborador.id_eyal == '17035'
    ).order_by(MetaColaborador.mes_ref.desc()).all()
    
    if metas:
        print(f"   Nome: {metas[0][2]}")
        print(f"   Metas cadastradas:")
        for mes, meta, nome in metas:
            print(f"   - {mes}: R$ {meta:,.2f}")
    else:
        print("   ❌ Colaborador não encontrado na tabela de metas")
    
    # Buscar realizado deste colaborador
    realizados = db.query(
        RealizadoColaborador.mes_ref,
        func.sum(RealizadoColaborador.total_realizado).label('total')
    ).filter(
        RealizadoColaborador.id_eyal == 17035
    ).group_by(
        RealizadoColaborador.mes_ref
    ).order_by(
        RealizadoColaborador.mes_ref.desc()
    ).all()
    
    if realizados:
        print(f"\n   Realizados cadastrados:")
        for mes, total in realizados:
            print(f"   - {mes}: R$ {total:,.2f}")
    else:
        print("\n   ❌ Sem dados de realizado para este colaborador")

except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "="*80 + "\n")

db.close()
