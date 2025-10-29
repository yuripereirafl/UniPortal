"""Script para verificar permissões de um usuário"""
from app.database import SessionLocal
# Importar todos os modelos para evitar erros de relacionamento
from app.models.grupos import Grupo
from app.models.usuario import Usuario
from app.models.permissao import Permissao
from app.models.usuarios_permissoes import usuarios_permissoes
from app.models.usuario_grupo import usuario_grupo
from app.models.grupo_permissao import grupo_permissao

def check_user_permissions(username):
    db = SessionLocal()
    try:
        # Buscar usuário
        user = db.query(Usuario).filter(Usuario.username == username).first()
        if not user:
            print(f"[X] Usuario '{username}' nao encontrado!")
            return
        
        print(f"\n[OK] Usuario encontrado:")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   ID Funcionario: {user.id_funcionario}")
        
        # Permissões diretas
        permissoes_direct = db.query(Permissao).join(usuarios_permissoes).filter(
            usuarios_permissoes.c.usuario_id == user.id
        ).all()
        
        print(f"\n[Permissoes Diretas] ({len(permissoes_direct)}):")
        for p in permissoes_direct:
            print(f"   - {p.codigo or p.descricao} (ID: {p.id})")
        
        # Permissões via grupos
        permissoes_via_grupo = db.query(Permissao).join(grupo_permissao).join(
            usuario_grupo, grupo_permissao.c.grupo_id == usuario_grupo.c.grupo_id
        ).filter(usuario_grupo.c.usuario_id == user.id).all()
        
        print(f"\n[Permissoes via Grupos] ({len(permissoes_via_grupo)}):")
        for p in permissoes_via_grupo:
            print(f"   - {p.codigo or p.descricao} (ID: {p.id})")
        
        # Total (deduplic)
        permissoes_map = {p.id: p for p in (permissoes_direct + permissoes_via_grupo)}
        permissoes_total = list(permissoes_map.values())
        
        print(f"\n[Total de Permissoes Unicas]: {len(permissoes_total)}")
        
        # Verificar se tem meta_colaborador
        def normalize_code(s):
            if not s:
                return ''
            return ''.join(ch for ch in str(s).strip().lower().replace(' ', '_') if (ch.isalnum() or ch == '_'))
        
        has_meta = any(
            normalize_code(p.codigo or p.descricao) == 'meta_colaborador'
            for p in permissoes_total
        )
        
        print(f"\n[Codigos Normalizados]:")
        for p in permissoes_total:
            print(f"   - '{p.codigo or p.descricao}' -> '{normalize_code(p.codigo or p.descricao)}'")
        
        if has_meta:
            print("\n[OK] Usuario TEM permissao 'meta_colaborador'")
            print("    O sistema deve redirecionar para a meta individual!")
        else:
            print("\n[X] Usuario NAO tem permissao 'meta_colaborador'")
            print("\n[INFO] Para adicionar a permissao:")
            print(f"   1. Va em 'Usuarios' no sistema")
            print(f"   2. Edite o usuario '{username}'")
            print(f"   3. Adicione a permissao 'Meta Colaborador'")
        
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    username = sys.argv[1] if len(sys.argv) > 1 else "02122131055"
    check_user_permissions(username)
