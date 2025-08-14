import sys
import os

# Adicionar o diretório pai ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import SessionLocal

def listar_usuarios():
    """Lista todos os usuários do banco"""
    db = SessionLocal()
    try:
        # Consulta SQL direta
        result = db.execute(text("""
            SELECT id, username, hashsenha 
            FROM rh_homologacao.usuarios 
            ORDER BY id
        """))
        
        usuarios = result.fetchall()
        
        print("=== USUÁRIOS NO BANCO ===")
        if not usuarios:
            print("❌ Nenhum usuário encontrado!")
            return []
        
        for user in usuarios:
            print(f"ID: {user[0]}, Username: '{user[1]}', Hash: {user[2][:50]}...")
        
        return usuarios
        
    except Exception as e:
        print(f"❌ Erro ao consultar usuários: {e}")
        return []
    finally:
        db.close()

def testar_conexao():
    """Testa se a conexão com o banco está funcionando"""
    db = SessionLocal()
    try:
        # Teste simples de conexão
        result = db.execute(text("SELECT 1 as test"))
        test = result.fetchone()
        
        if test[0] == 1:
            print("✅ Conexão com o banco está funcionando!")
            return True
        else:
            print("❌ Problema na conexão com o banco!")
            return False
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=== TESTE DE BANCO DE DADOS ===")
    
    # Testar conexão
    if not testar_conexao():
        print("Não foi possível conectar ao banco!")
        sys.exit(1)
    
    # Listar usuários
    usuarios = listar_usuarios()
    
    if usuarios:
        print(f"\n✅ Encontrados {len(usuarios)} usuários no banco!")
        print("\n💡 Para fazer login, use um dos usernames acima.")
        print("💡 Se não souber a senha, ela pode ser 'admin', '123456' ou o próprio username.")
    else:
        print("\n⚠️ Nenhum usuário encontrado! Você precisa criar usuários primeiro.")
