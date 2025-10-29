"""
Script rápido para associar a permissão 'adm' a um usuário pelo username.
Uso: python grant_admin_to_user.py <username>

Ele conecta usando a mesma configuração de `app.database` e faz:
- procura usuário por username no schema rh_homologacao.usuarios
- procura permissão com codigo 'adm' (na tabela permissões)
- se não existir, mostra erro (não cria automaticamente)
- insere em usuarios_permissoes (se ainda não existir)

ATENÇÃO: rodar isso em ambientes controlados apenas.
"""
import sys
from sqlalchemy import text
from app.database import engine

if len(sys.argv) < 2:
    print("Usage: python grant_admin_to_user.py <username>")
    sys.exit(1)

username = sys.argv[1]
with engine.connect() as conn:
    # achar usuário
    user_row = conn.execute(text("SELECT id, username FROM rh_homologacao.usuarios WHERE username = :u"), {"u": username}).fetchone()
    if not user_row:
        print(f"Usuário '{username}' não encontrado")
        sys.exit(1)
    user_id = user_row[0]
    print(f"Found user id={user_id} username={user_row[1]}")

    # achar permissao adm (codigo 'adm' ou 'ADM' - case insensitive)
    perm_row = conn.execute(text("SELECT id, codigo FROM permissoes WHERE lower(codigo) = 'adm' LIMIT 1")).fetchone()
    if not perm_row:
        print("Permissão 'adm' não encontrada na tabela 'permissoes'. Verifique os códigos existentes.")
        sys.exit(1)
    perm_id = perm_row[0]
    print(f"Found permissao id={perm_id} codigo={perm_row[1]}")

    # verificar se já existe
    exists = conn.execute(text("SELECT 1 FROM usuarios_permissoes WHERE usuario_id = :uid AND permissao_id = :pid"), {"uid": user_id, "pid": perm_id}).fetchone()
    if exists:
        print("Associação já existe, nada a fazer.")
        sys.exit(0)

    # inserir
    conn.execute(text("INSERT INTO usuarios_permissoes (usuario_id, permissao_id) VALUES (:uid, :pid)"), {"uid": user_id, "pid": perm_id})
    conn.commit()
    print("Permissão 'adm' concedida ao usuário com sucesso.")
