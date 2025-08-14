import sqlite3
import os

# Conecta ao banco de dados
db_path = os.path.join(os.path.dirname(__file__), 'system_ti.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 60)
print("TESTANDO CONSULTAS DE USUÁRIOS")
print("=" * 60)

# 1. Verificar se a tabela usuarios existe e seus dados
print("\n1. TABELA USUARIOS:")
print("-" * 40)
try:
    cursor.execute("SELECT * FROM usuarios LIMIT 10")
    usuarios = cursor.fetchall()
    
    # Pegar nomes das colunas
    cursor.execute("PRAGMA table_info(usuarios)")
    colunas = [col[1] for col in cursor.fetchall()]
    print(f"Colunas: {', '.join(colunas)}")
    
    if usuarios:
        for usuario in usuarios:
            print(f"Usuário: {usuario}")
    else:
        print("Nenhum usuário encontrado na tabela 'usuarios'")
except Exception as e:
    print(f"Erro ao consultar tabela usuarios: {e}")

# 2. Verificar tabela usuario_grupo
print("\n2. RELACIONAMENTO USUARIO-GRUPO:")
print("-" * 40)
try:
    cursor.execute("""
        SELECT u.id, u.username, g.id as grupo_id, g.nome as grupo_nome
        FROM usuarios u
        LEFT JOIN usuario_grupo ug ON u.id = ug.usuario_id
        LEFT JOIN grupos g ON ug.grupo_id = g.id
        ORDER BY u.id
    """)
    resultado = cursor.fetchall()
    
    if resultado:
        for row in resultado:
            print(f"User ID: {row[0]}, Username: {row[1]}, Grupo ID: {row[2]}, Grupo: {row[3]}")
    else:
        print("Nenhum relacionamento usuario-grupo encontrado")
except Exception as e:
    print(f"Erro ao consultar usuario-grupo: {e}")

# 3. Verificar tabela usuario_unidade
print("\n3. RELACIONAMENTO USUARIO-UNIDADE:")
print("-" * 40)
try:
    cursor.execute("""
        SELECT u.id, u.username, f.id as filial_id, f.unidade
        FROM usuarios u
        LEFT JOIN usuario_unidade uu ON u.id = uu.usuario_id
        LEFT JOIN filial f ON uu.filial_id = f.id
        ORDER BY u.id
    """)
    resultado = cursor.fetchall()
    
    if resultado:
        for row in resultado:
            print(f"User ID: {row[0]}, Username: {row[1]}, Filial ID: {row[2]}, Unidade: {row[3]}")
    else:
        print("Nenhum relacionamento usuario-unidade encontrado")
except Exception as e:
    print(f"Erro ao consultar usuario-unidade: {e}")

# 4. Consulta completa (igual ao backend)
print("\n4. CONSULTA COMPLETA (COMO NO BACKEND):")
print("-" * 40)
try:
    cursor.execute("SELECT id, username FROM usuarios")
    usuarios = cursor.fetchall()
    
    for usuario in usuarios:
        user_id = usuario[0]
        username = usuario[1]
        
        # Buscar grupos
        cursor.execute("""
            SELECT g.id, g.nome
            FROM grupos g
            JOIN usuario_grupo ug ON g.id = ug.grupo_id
            WHERE ug.usuario_id = ?
        """, (user_id,))
        grupos = cursor.fetchall()
        
        # Buscar unidades
        cursor.execute("""
            SELECT f.id, f.unidade
            FROM usuario_unidade uu
            JOIN filial f ON uu.filial_id = f.id
            WHERE uu.usuario_id = ?
        """, (user_id,))
        unidades = cursor.fetchall()
        
        print(f"\nUsuário: {username} (ID: {user_id})")
        print(f"  Grupos: {grupos}")
        print(f"  Unidades: {unidades}")
        
except Exception as e:
    print(f"Erro na consulta completa: {e}")

# 5. Verificar tabelas auxiliares
print("\n5. VERIFICAR DADOS AUXILIARES:")
print("-" * 40)

print("Grupos disponíveis:")
try:
    cursor.execute("SELECT id, nome FROM grupos LIMIT 5")
    grupos = cursor.fetchall()
    for grupo in grupos:
        print(f"  ID: {grupo[0]}, Nome: {grupo[1]}")
except Exception as e:
    print(f"Erro ao consultar grupos: {e}")

print("\nFiliais disponíveis:")
try:
    cursor.execute("SELECT id, unidade FROM filial LIMIT 5")
    filiais = cursor.fetchall()
    for filial in filiais:
        print(f"  ID: {filial[0]}, Unidade: {filial[1]}")
except Exception as e:
    print(f"Erro ao consultar filiais: {e}")

# 6. Contar registros
print("\n6. CONTAGEM DE REGISTROS:")
print("-" * 40)
try:
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total_usuarios = cursor.fetchone()[0]
    print(f"Total de usuários: {total_usuarios}")
    
    cursor.execute("SELECT COUNT(*) FROM usuario_grupo")
    total_usuario_grupo = cursor.fetchone()[0]
    print(f"Total de vínculos usuario-grupo: {total_usuario_grupo}")
    
    cursor.execute("SELECT COUNT(*) FROM usuario_unidade")
    total_usuario_unidade = cursor.fetchone()[0]
    print(f"Total de vínculos usuario-unidade: {total_usuario_unidade}")
    
except Exception as e:
    print(f"Erro ao contar registros: {e}")

conn.close()
print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)
