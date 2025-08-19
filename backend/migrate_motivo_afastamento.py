#!/usr/bin/env python3
"""
Script para adicionar a coluna motivo_afastamento na tabela funcionarios
"""

from sqlalchemy import create_engine, text

# Configuração do banco (ajuste conforme sua configuração)
DATABASE_URL = "postgresql://postgres:123@localhost:5432/rh_homologacao"

def run_migration():
    """Executa a migração para adicionar coluna motivo_afastamento"""
    engine = create_engine(DATABASE_URL)
    
    migration_sql = """
    -- Adicionar a coluna motivo_afastamento na tabela funcionarios
    ALTER TABLE rh_homologacao.funcionarios 
    ADD COLUMN IF NOT EXISTS motivo_afastamento TEXT;
    
    -- Criar índice para buscas por funcionários com afastamento
    CREATE INDEX IF NOT EXISTS idx_funcionarios_afastamento 
        ON rh_homologacao.funcionarios(data_afastamento) 
        WHERE data_afastamento IS NOT NULL;
    """
    
    try:
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text(migration_sql))
                print("✅ Migração executada com sucesso!")
                print("✅ Coluna 'motivo_afastamento' adicionada na tabela funcionarios")
                print("✅ Índice criado para data_afastamento")
    except Exception as e:
        print(f"❌ Erro ao executar migração: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    run_migration()
