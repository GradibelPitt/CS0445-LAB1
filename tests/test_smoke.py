from fastapi.testclient import TestClient
from app.main import app, init_db

def test_places():
    init_db(); c=TestClient(app); r=c.get('/api/places'); assert r.status_code==200; assert len(r.json())>=10
