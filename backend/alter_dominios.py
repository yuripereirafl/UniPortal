import sys
from pathlib import Path

# Fix import path for running from backend folder
sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine
from sqlalchemy import text

print("Adicionando coluna provedor...")
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE dominios ADD COLUMN provedor VARCHAR;"))
        conn.commit()
    print("Coluna adicionada com sucesso!")
except Exception as e:
    print(f"Erro: {e}")
