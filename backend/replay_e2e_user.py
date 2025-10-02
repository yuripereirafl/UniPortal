from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.usuario import Usuario

client = TestClient(app)

db = SessionLocal()
user = db.query(Usuario).filter(Usuario.username.like('e2e_test_user%')).order_by(Usuario.id.desc()).first()
db.close()

if not user:
    print('Nenhum usuário e2e_test_user encontrado no banco.')
    raise SystemExit(1)

username = user.username
password = 'Test1234!'
print('Replay para usuário:', username)

resp = client.post('/login', data={"username": username, "password": password})
print('POST /login ->', resp.status_code)
try:
    print(resp.json())
except Exception:
    print(resp.text)

if resp.status_code != 200:
    raise SystemExit('Login falhou')

token = resp.json().get('access_token')
headers = {"Authorization": f"Bearer {token}"}
resp = client.get('/me', headers=headers)
print('GET /me ->', resp.status_code)
try:
    print(resp.json())
except Exception:
    print(resp.text)
