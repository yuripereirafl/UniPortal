import os
import sys
from pathlib import Path

# Adicionar o diretório backend ao path para encontrar os módulos
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import engine
from app.models.base import Base
from app.models.sistema import Sistema
from app.models.setor import Setor
from app.models.funcionario import Funcionario
from app.models.celular import CelularLinha, CelularConta
from sqlalchemy import text

def init_tables():
    print("🚀 Iniciando criação das tabelas de Celulares...")
    try:
        # Garantir que o schema rh_homologacao existe
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS rh_homologacao;"))
            conn.commit()
            print("✅ Schema 'rh_homologacao' verificado/criado.")

        # Criar tabelas
        Base.metadata.create_all(bind=engine, tables=[
            CelularLinha.__table__,
            CelularConta.__table__
        ])
        print("✅ Tabelas 'celulares_linhas' e 'celulares_contas' criadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")

if __name__ == "__main__":
    init_tables()
