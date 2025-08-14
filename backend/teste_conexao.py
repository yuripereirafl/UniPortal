import psycopg2

# Teste de conexão direta ao PostgreSQL
def testar_conexao_direta():
    try:
        print("Tentando conectar ao banco PostgreSQL...")
        
        conn = psycopg2.connect(
            host='192.168.1.37',
            database='dadosrh',
            user='dadosrh',
            password='dadosrh',
            port=5432
        )
        
        print("✅ Conexão estabelecida com sucesso!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM rh_homologacao.usuarios LIMIT 5")
        usuarios = cursor.fetchall()
        
        print(f"✅ Encontrados {len(usuarios)} usuários:")
        for user in usuarios:
            print(f"  - ID: {user[0]}, Username: '{user[1]}'")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

if __name__ == "__main__":
    testar_conexao_direta()
