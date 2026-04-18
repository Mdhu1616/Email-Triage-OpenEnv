from starlette.testclient import TestClient
from app import create_app
app = create_app()
client = TestClient(app)
r = client.post('/api/reset', json={'task_id':'easy_categorization','seed':42})
print('status', r.status_code, r.json())
print('health', client.get('/health').status_code, client.get('/health').json())
