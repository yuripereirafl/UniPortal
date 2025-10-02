from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

username = f"test_integ_{int(time.time())}"
password = "Test1234!"

print('Criando usuário de teste:', username)
resp = client.post('/usuarios/', json={"username": username, "password": password})
print('POST /usuarios/ ->', resp.status_code, resp.text)

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
