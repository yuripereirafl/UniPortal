import psycopg2
import requests

# Configuração do banco PostgreSQL
DB_CONFIG = {
    'host': '192.168.1.37',
    'database': 'dadosrh',
    'user': 'dadosrh',
    'password': 'dadosrh',
    'port': 5432
}

def conectar_banco():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erro ao conectar no banco: {e}")
        return None

def listar_usuarios():
    conn = conectar_banco()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, hashsenha FROM rh_homologacao.usuarios")
        usuarios = cursor.fetchall()
        
        print("\n=== USUÁRIOS NO BANCO ===")
        for user in usuarios:
            print(f"ID: {user[0]}, Username: {user[1]}, Hash: {user[2][:50]}...")
        
        conn.close()
        return usuarios
        
    except Exception as e:
        print(f"Erro ao consultar usuários: {e}")
        conn.close()
        return []

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

if __name__ == "__main__":
    print("=== TESTE DE LOGIN ===")
    
    # Listar usuários existentes
    usuarios = listar_usuarios()
    
    if not usuarios:
        print("⚠️ Nenhum usuário encontrado no banco!")
        print("Vamos tentar algumas credenciais padrão...")
        
        # Testar credenciais comuns
        credenciais_teste = [
            ("admin", "admin"),
            ("admin", "123456"),
            ("admin", "password"),
            ("user", "user"),
            ("test", "test")
        ]
        
        for username, password in credenciais_teste:
            print(f"\n🧪 Testando: {username}/{password}")
            if testar_login(username, password):
                print(f"✅ Login funcionou com: {username}/{password}")
                break
        else:
            print("❌ Nenhuma credencial funcionou!")
    else:
        # Testar com primeiro usuário
        primeiro_usuario = usuarios[0]
        print(f"\n🧪 Testando login com usuário: {primeiro_usuario[1]}")
        
        # Tentar algumas senhas comuns
        senhas_teste = ["admin", "123456", "password", primeiro_usuario[1]]
        
        for senha in senhas_teste:
            print(f"\nTentando senha: {senha}")
            if testar_login(primeiro_usuario[1], senha):
                print(f"✅ Senha correta: {senha}")
                break
        else:
            print("❌ Nenhuma senha funcionou!")
