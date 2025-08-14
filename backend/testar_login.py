import requests
import sys

# Testar login
def testar_login(username, password):
    try:
        url = "http://localhost:8000/login"
        data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(url, data=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return True
        else:
            print("❌ Login failed!")
            return False
            
    except Exception as e:
        print(f"Erro ao testar login: {e}")
        return False

# Listar usuários do banco
def listar_usuarios():
    try:
        from app.database import SessionLocal
        from app.models.user import User
        
        db = SessionLocal()
        usuarios = db.query(User).all()
        
        print("\n=== USUÁRIOS NO BANCO ===")
        for user in usuarios:
            print(f"ID: {user.id}, Username: {user.username}, Hash: {user.hashsenha[:50]}...")
        
        db.close()
        return usuarios
        
    except Exception as e:
        print(f"Erro ao listar usuários: {e}")
        return []

if __name__ == "__main__":
    print("=== TESTE DE LOGIN ===")
    
    # Listar usuários existentes
    usuarios = listar_usuarios()
    
    if not usuarios:
        print("⚠️ Nenhum usuário encontrado no banco!")
        sys.exit(1)
    
    # Testar com primeiro usuário
    primeiro_usuario = usuarios[0]
    print(f"\n🧪 Testando login com usuário: {primeiro_usuario.username}")
    
    # Tentar algumas senhas comuns
    senhas_teste = ["admin", "123456", "password", primeiro_usuario.username]
    
    for senha in senhas_teste:
        print(f"\nTentando senha: {senha}")
        if testar_login(primeiro_usuario.username, senha):
            print(f"✅ Senha correta: {senha}")
            break
    else:
        print("❌ Nenhuma senha funcionou!")
