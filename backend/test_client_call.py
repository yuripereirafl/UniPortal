from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

resp = client.get('/usuarios/')
print('STATUS', resp.status_code)
try:
    print(resp.json())
except Exception:
    print(resp.text)
