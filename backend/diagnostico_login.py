#!/usr/bin/env python3
import sys
import os
import requests
from passlib.context import CryptContext

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.usuario import Usuario

def verificar_usuarios_e_senhas():
    """Verifica usuários no banco e testa as senhas"""
    
    print("=== DIAGNÓSTICO DE LOGIN ===\n")
    
    # Conectar ao banco
    db = SessionLocal()
    
    try:
        # Buscar todos os usuários
        usuarios = db.query(Usuario).all()
        
        if not usuarios:
            print("❌ Nenhum usuário encontrado no banco!")
            return
        
        print(f"✅ Encontrados {len(usuarios)} usuários:")
        
        # Configurar o contexto de criptografia (mesmo do sistema)
        pwd_context = CryptContext(schemes=["sha512_crypt", "sha256_crypt"], deprecated="auto")
        
        for usuario in usuarios:
            print(f"\n👤 Usuário: {usuario.username}")
            print(f"   ID: {usuario.id}")
            print(f"   Hash: {usuario.hashsenha[:50]}...")
            
            # Testar senhas comuns
            senhas_teste = ["admin", "123456", "password", usuario.username, "dadosrh"]
            
            senha_encontrada = False
            for senha in senhas_teste:
                try:
                    if pwd_context.verify(senha, usuario.hashsenha):
                        print(f"   ✅ SENHA CORRETA: '{senha}'")
                        senha_encontrada = True
                        
                        # Testar login via API
                        print(f"   🧪 Testando login via API...")
                        response = requests.post(
                            "http://localhost:8000/login",
                            data={"username": usuario.username, "password": senha},
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            print(f"   ✅ LOGIN API FUNCIONOU!")
                        else:
                            print(f"   ❌ LOGIN API FALHOU: {response.status_code} - {response.text}")
                        
                        break
                except Exception as e:
                    continue
            
            if not senha_encontrada:
                print(f"   ❌ Nenhuma senha testada funcionou")
                
        # Testar se o endpoint está respondendo
        print(f"\n🔗 Testando conectividade com o backend...")
        try:
            response = requests.get("http://localhost:8000/verificar-permissao", timeout=5)
            if response.status_code == 200:
                print(f"✅ Backend está respondendo: {response.json()}")
            else:
                print(f"❌ Backend problema: {response.status_code}")
        except Exception as e:
            print(f"❌ Erro ao conectar backend: {e}")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verificar_usuarios_e_senhas()
