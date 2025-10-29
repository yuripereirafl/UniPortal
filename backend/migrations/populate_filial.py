"""
Script para popular a coluna 'filial' na tabela basecampanhas
com base nos dados de metas_colaboradores

Executar: python backend/migrations/populate_filial.py
"""

import sys
from pathlib import Path

# Adicionar o diretório backend ao path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.database import engine

def populate_filial():
    """
    Atualiza a coluna 'filial' na tabela basecampanhas
    com base na unidade do colaborador em metas_colaboradores
    """
    
    print("🔄 Iniciando população da coluna 'filial'...")
    
    with engine.connect() as conn:
        # Query para atualizar filial com base em metas_colaboradores
        update_query = text("""
            UPDATE rh_homologacao.basecampanhas AS bc
            SET filial = mc.unidade
            FROM rh_homologacao.metas_colaboradores AS mc
            WHERE bc.cod_usuario = mc.id_eyal
              AND EXTRACT(YEAR FROM bc.mes) = EXTRACT(YEAR FROM mc.mes_ref)
              AND EXTRACT(MONTH FROM bc.mes) = EXTRACT(MONTH FROM mc.mes_ref)
              AND bc.filial IS NULL;
        """)
        
        print("📊 Executando UPDATE...")
        result = conn.execute(update_query)
        rows_updated = result.rowcount
        
        print(f"✅ {rows_updated} registros atualizados com sucesso!")
        
        # Verificar quantos registros ainda estão NULL
        check_query = text("""
            SELECT COUNT(*) as total_null
            FROM rh_homologacao.basecampanhas
            WHERE filial IS NULL;
        """)
        
        result = conn.execute(check_query)
        total_null = result.fetchone()[0]
        
        if total_null > 0:
            print(f"⚠️  Ainda há {total_null} registros com filial NULL")
            print("   Isso pode ser porque o cod_usuario não existe em metas_colaboradores")
        else:
            print("🎉 Todos os registros foram populados!")
        
        conn.commit()
    
    print("\n✅ Migração concluída!")

if __name__ == "__main__":
    try:
        populate_filial()
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
