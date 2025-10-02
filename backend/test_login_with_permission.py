from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.permissao import Permissao
from app.models.usuarios_permissoes import usuarios_permissoes
from app.models.usuario import Usuario as UsuarioModel
import time

client = TestClient(app)

username = f"test_perm_{int(time.time())}"
password = "Test1234!"

print('Criando usuário de teste:', username)
resp = client.post('/usuarios/', json={"username": username, "password": password})
print('POST /usuarios/ ->', resp.status_code, resp.text)

db = SessionLocal()
# procurar permissão 'Meta Colaborador' por codigo ou descricao
perm = db.query(Permissao).filter((Permissao.codigo == 'Meta Colaborador') | (Permissao.descricao.ilike('%meta colaborador%'))).first()
if not perm:
    print('Permissão "Meta Colaborador" não encontrada no banco. Saindo.')
    db.close()
    raise SystemExit(1)

print('Encontrada permissão:', perm.id, perm.codigo, perm.descricao)

# inserir associação na tabela usuarios_permissoes
# localizar o usuário criado via ORM
user = db.query(UsuarioModel).filter(UsuarioModel.username == username).first()
if not user:
    print('Não localizei o usuário no DB após criação')
    db.close()
    raise SystemExit(1)
user_id = user.id
print('ID do usuário criado:', user_id)

# inserir associação na tabela usuarios_permissoes
db.execute(usuarios_permissoes.insert().values(usuario_id=user_id, permissao_id=perm.id))
db.commit()
db.close()

print('\nTentando login com /login (form)')
resp = client.post('/login', data={"username": username, "password": password})
print('POST /login ->', resp.status_code)
try:
    print(resp.json())
except Exception:
    print(resp.text)

if resp.status_code != 200:
    raise SystemExit('Login falhou, abortando')

token = resp.json().get('access_token')
headers = {"Authorization": f"Bearer {token}"}

print('\nChamando /me com o token obtido')
resp = client.get('/me', headers=headers)
print('GET /me ->', resp.status_code)
try:
    print(resp.json())
except Exception:
    print(resp.text)
