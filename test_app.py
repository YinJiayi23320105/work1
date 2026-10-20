import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_api(client):
    # 测试登录接口，获取JWT
    resp = client.post("/login", json={"username":"admin", "password":"123456"})
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert "access_token" in json_data

def test_protected_api_no_token(client):
    # 无token访问受保护接口，应该返回401
    resp = client.get("/protected")
    assert resp.status_code == 401

def test_protected_with_token(client):
    # 拿到token再访问保护接口
    login_resp = client.post("/login", json={"username":"admin", "password":"123456"})
    token = login_resp.get_json()["access_token"]
    resp = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
