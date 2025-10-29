"""
Script para verificar se as vendas estão vindo da tabela basecampanhas
"""
import sys
sys.path.append('.')

from app.database import engine
from sqlalchemy import text

print("=" * 80)
print("VERIFICAÇÃO DE VENDAS - BASECAMPANHAS vs REALIZADO_COLABORADOR")
print("=" * 80)

with engine.connect() as conn:
    # 1. Verificar total de registros em basecampanhas
    print("\n1. TABELA: rh_homologacao.basecampanhas (Fonte Original)")
    print("-" * 80)
    try:
        result = conn.execute(text("SELECT COUNT(*) as total FROM rh_homologacao.basecampanhas"))
        total_basecampanhas = result.scalar()
        print(f"   Total de registros: {total_basecampanhas:,}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # 2. Verificar total em realizado_colaborador
    print("\n2. TABELA: rh_homologacao.realizado_colaborador (Dados Agregados)")
    print("-" * 80)
    result = conn.execute(text("SELECT COUNT(*) as total FROM rh_homologacao.realizado_colaborador"))
    total_realizado = result.scalar()
    print(f"   Total de registros: {total_realizado:,}")
    
    # 3. Verificar dados da ANDRIELE (ID 17035)
    print("\n3. DADOS DA ANDRIELE RAMOS LEONARDO (ID Eyal: 17035)")
    print("-" * 80)
    
    # Verificar em basecampanhas
    print("\n   A) Vendas em basecampanhas (Setembro 2024):")
    try:
        query = text("""
            SELECT 
                grupo_exames,
                COUNT(*) as quantidade,
                SUM(valor_original_proc) as total_valor
            FROM rh_homologacao.basecampanhas
            WHERE cod_usuario = '17035'
              AND EXTRACT(YEAR FROM mes) = 2024
              AND EXTRACT(MONTH FROM mes) = 9
            GROUP BY grupo_exames
            ORDER BY grupo_exames
        """)
        result = conn.execute(query)
        rows = result.fetchall()
        
        if rows:
            total_geral = 0
            for row in rows:
                grupo = row[0] or 'SEM GRUPO'
                qtd = row[1]
                valor = float(row[2]) if row[2] else 0
                total_geral += valor
                print(f"      {grupo:20} | Qtd: {qtd:4} | Valor: R$ {valor:,.2f}")
            print(f"      {'TOTAL GERAL':20} |          | Valor: R$ {total_geral:,.2f}")
        else:
            print("      ⚠️ Nenhum registro encontrado em basecampanhas")
    except Exception as e:
        print(f"      ❌ Erro ao buscar em basecampanhas: {e}")
    
    # Verificar em realizado_colaborador
    print("\n   B) Dados em realizado_colaborador (Setembro 2024):")
    query = text("""
        SELECT 
            tipo_grupo,
            SUM(total_registros) as quantidade,
            SUM(total_realizado) as total_valor
        FROM rh_homologacao.realizado_colaborador
        WHERE id_eyal = 17035
          AND mes_ref = '2024-09-01'
        GROUP BY tipo_grupo
        ORDER BY tipo_grupo
    """)
    result = conn.execute(query)
    rows = result.fetchall()
    
    if rows:
        total_geral = 0
        for row in rows:
            tipo = row[0] or 'SEM TIPO'
            qtd = row[1] or 0
            valor = float(row[2]) if row[2] else 0
            total_geral += valor
            print(f"      {tipo:20} | Qtd: {qtd:4} | Valor: R$ {valor:,.2f}")
        print(f"      {'TOTAL GERAL':20} |          | Valor: R$ {total_geral:,.2f}")
    else:
        print("      ⚠️ Nenhum registro encontrado em realizado_colaborador")
    
    # 4. Verificar estrutura das tabelas
    print("\n4. ESTRUTURA DAS TABELAS")
    print("-" * 80)
    
    print("\n   A) Campos de basecampanhas:")
    try:
        query = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema IN ('rh_homologacao', 'rh')
              AND table_name = 'basecampanhas'
            ORDER BY ordinal_position
            LIMIT 15
        """)
        result = conn.execute(query)
        for row in result:
            print(f"      - {row[0]:30} ({row[1]})")
    except Exception as e:
        print(f"      ❌ Erro: {e}")
    
    print("\n   B) Campos de realizado_colaborador:")
    query = text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'rh_homologacao' 
          AND table_name = 'realizado_colaborador'
        ORDER BY ordinal_position
    """)
    result = conn.execute(query)
    for row in result:
        print(f"      - {row[0]:30} ({row[1]})")

    # 5. Verificar se existe view ou trigger que alimenta realizado_colaborador
    print("\n5. VERIFICAÇÃO DE ETL/PROCESSO DE CARGA")
    print("-" * 80)
    
    # Verificar data de atualização
    query = text("""
        SELECT 
            MAX(data_atualizacao) as ultima_atualizacao,
            COUNT(DISTINCT mes_ref) as qtd_meses,
            MIN(mes_ref) as mes_mais_antigo,
            MAX(mes_ref) as mes_mais_recente
        FROM rh_homologacao.realizado_colaborador
    """)
    result = conn.execute(query)
    row = result.fetchone()
    
    print(f"   Última atualização: {row[0]}")
    print(f"   Quantidade de meses: {row[1]}")
    print(f"   Período: {row[2]} até {row[3]}")

print("\n" + "=" * 80)
print("CONCLUSÃO:")
print("=" * 80)
print("""
A tabela 'realizado_colaborador' é uma TABELA AGREGADA que contém dados
pré-processados, provavelmente alimentada por um processo ETL que lê da
tabela 'basecampanhas' (ou diretamente do sistema Eyal) e:

1. Agrupa vendas por: id_eyal, mes_ref, tipo_grupo, unidade
2. Soma os valores (total_realizado)
3. Conta os registros (total_registros)
4. Armazena em rh_homologacao.realizado_colaborador

Os dados exibidos na tela VÊEM de 'realizado_colaborador', NÃO diretamente
de 'basecampanhas'. A API /vendas busca em 'basecampanhas', mas não está
sendo usada no componente MetaColaborador.vue atual.
""")
print("=" * 80)
