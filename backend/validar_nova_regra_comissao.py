import sys
sys.stdout.reconfigure(encoding='utf-8')

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "dadosrh")
DB_PASSWORD = os.getenv("DB_PASSWORD", "dadosrh")
DB_NAME = os.getenv("DB_NAME", "dadosrh")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL)

print("="*80)
print("✅ VALIDAÇÃO: NOVA REGRA DE COMISSÃO PARA COORDENADORES")
print("="*80)

with engine.connect() as conn:
    
    # 1. Total de vendas da filial (novo método)
    print(f"\n1️⃣ MÉTODO NOVO - Por FILIAL (coordenadores/gerentes):")
    result = conn.execute(text("""
        SELECT COUNT(*) as total
        FROM rh_homologacao.basecampanhas
        WHERE filial = 'CENTRAL DE MARCACÕES'
          AND EXTRACT(year FROM mes) = 2025
          AND EXTRACT(month FROM mes) = 10
    """))
    vendas_por_filial = result.fetchone()[0]
    print(f"   Total de vendas na filial: {vendas_por_filial}")
    
    # 2. Vendas por status em metas_colaboradores
    print(f"\n2️⃣ Detalhamento das {vendas_por_filial} vendas:")
    
    # Com meta
    result = conn.execute(text("""
        SELECT COUNT(*) as total
        FROM rh_homologacao.basecampanhas b
        WHERE filial = 'CENTRAL DE MARCACÕES'
          AND EXTRACT(year FROM mes) = 2025
          AND EXTRACT(month FROM mes) = 10
          AND EXISTS (
              SELECT 1
              FROM rh_homologacao.metas_colaboradores m
              WHERE m.id_eyal = b.cod_usuario
                AND m.mes_ref = '2025-10-01'
          )
    """))
    vendas_com_meta = result.fetchone()[0]
    
    # Sem meta
    result = conn.execute(text("""
        SELECT COUNT(*) as total
        FROM rh_homologacao.basecampanhas b
        WHERE filial = 'CENTRAL DE MARCACÕES'
          AND EXTRACT(year FROM mes) = 2025
          AND EXTRACT(month FROM mes) = 10
          AND NOT EXISTS (
              SELECT 1
              FROM rh_homologacao.metas_colaboradores m
              WHERE m.id_eyal = b.cod_usuario
                AND m.mes_ref = '2025-10-01'
          )
    """))
    vendas_sem_meta = result.fetchone()[0]
    
    print(f"   ├─ Colaboradores COM meta:  {vendas_com_meta} vendas")
    print(f"   └─ Colaboradores SEM meta:  {vendas_sem_meta} vendas (DESLIGADOS/NÃO CADASTRADOS)")
    
    # 3. Detalhes dos desligados/não cadastrados
    if vendas_sem_meta > 0:
        print(f"\n3️⃣ Colaboradores SEM meta que venderam:")
        result = conn.execute(text("""
            SELECT 
                b.cod_usuario,
                b.usuario_agendo,
                COUNT(*) as qtd,
                STRING_AGG(DISTINCT b.grupo_exames, ', ') as grupos
            FROM rh_homologacao.basecampanhas b
            WHERE filial = 'CENTRAL DE MARCACÕES'
              AND EXTRACT(year FROM mes) = 2025
              AND EXTRACT(month FROM mes) = 10
              AND NOT EXISTS (
                  SELECT 1
                  FROM rh_homologacao.metas_colaboradores m
                  WHERE m.id_eyal = b.cod_usuario
                    AND m.mes_ref = '2025-10-01'
              )
            GROUP BY b.cod_usuario, b.usuario_agendo
            ORDER BY qtd DESC
        """))
        
        for cod_usuario, usuario_agendo, qtd, grupos in result.fetchall():
            print(f"\n   ID: {cod_usuario} - {usuario_agendo}")
            print(f"   ├─ Vendas: {qtd}")
            print(f"   └─ Grupos: {grupos}")
            
            # Verificar histórico
            result2 = conn.execute(text("""
                SELECT mes_ref, cargo
                FROM rh_homologacao.metas_colaboradores
                WHERE id_eyal = :id
                ORDER BY mes_ref DESC
                LIMIT 1
            """), {"id": cod_usuario})
            
            historico = result2.fetchone()
            if historico:
                mes, cargo = historico
                print(f"      ℹ️ Último registro: {mes} ({cargo})")
                print(f"      📋 Status: DESLIGADO em outubro")
            else:
                print(f"      ⚠️ NUNCA teve meta cadastrada")
    
    # 4. Comparação com método antigo
    print(f"\n4️⃣ Comparação de Métodos:")
    
    # Método antigo: IDs com meta
    result = conn.execute(text("""
        SELECT COUNT(DISTINCT m.id_eyal)
        FROM rh_homologacao.metas_colaboradores m
        WHERE m.mes_ref = '2025-10-01'
          AND m.unidade = 'CENTRAL DE MARCACÕES'
    """))
    ids_com_meta = result.fetchone()[0]
    
    result = conn.execute(text("""
        SELECT COUNT(*)
        FROM rh_homologacao.basecampanhas b
        WHERE EXTRACT(year FROM mes) = 2025
          AND EXTRACT(month FROM mes) = 10
          AND EXISTS (
              SELECT 1
              FROM rh_homologacao.metas_colaboradores m
              WHERE m.id_eyal = b.cod_usuario
                AND m.mes_ref = '2025-10-01'
                AND m.unidade = 'CENTRAL DE MARCACÕES'
          )
    """))
    vendas_metodo_antigo = result.fetchone()[0]
    
    print(f"   Método ANTIGO (por IDs com meta):")
    print(f"   ├─ IDs considerados: {ids_com_meta}")
    print(f"   └─ Vendas encontradas: {vendas_metodo_antigo}")
    
    print(f"\n   Método NOVO (por FILIAL):")
    print(f"   ├─ IDs considerados: TODOS que venderam na filial")
    print(f"   └─ Vendas encontradas: {vendas_por_filial}")
    
    print(f"\n   📊 Ganho: +{vendas_por_filial - vendas_metodo_antigo} vendas")
    
    # 5. Validação com Excel
    print(f"\n5️⃣ Validação com Excel:")
    print(f"   Excel reporta:     310 vendas")
    print(f"   Sistema encontra:  {vendas_por_filial} vendas")
    
    diferenca = abs(310 - vendas_por_filial)
    if diferenca == 0:
        print(f"   ✅ PERFEITO! Sistema bate com Excel")
    elif diferenca <= 2:
        print(f"   ⚠️ Diferença mínima: {diferenca} vendas (tolerável)")
    else:
        print(f"   ❌ Diferença significativa: {diferenca} vendas")

print("\n" + "="*80)
print("💡 CONCLUSÃO:")
print("="*80)
print(f"✅ Coordenadores agora recebem comissão sobre TODAS vendas da filial")
print(f"✅ Inclui colaboradores desligados durante o mês")
print(f"✅ Inclui colaboradores nunca cadastrados em metas")
print(f"✅ Total: {vendas_por_filial} vendas (vs {vendas_metodo_antigo} no método antigo)")
print("="*80)
