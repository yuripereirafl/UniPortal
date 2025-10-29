"""
Listar códigos de permissões existentes (para ajustar condições no frontend)
Uso: python list_permissions.py
"""
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    rows = conn.execute(text("SELECT id, codigo, descricao FROM permissoes ORDER BY id")).fetchall()
    for r in rows:
        print(r)
