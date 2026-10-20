import pytest
from app import app
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        # 延迟导入，避免循环导入问题
        from app import db, User
        db.create_all()
        hashed_pw = generate_password_hash("123456").decode("utf-8")
        test_user = User(username="admin", password=hashed_pw)
        db.session.add(test_user)
        db.session.commit()
        with app.test_client() as client:
            yield client
        db.session.remove()
        db.drop_all()


def test_login_api(client):
    resp = client.post("/auth/login", json={"username":"admin", "password":"123456"})
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert "access_token" in json_data

def test_protected_api_no_token(client):
    resp = client.get("/api/data")
    assert resp.status_code == 401

def test_protected_with_token(client):
    login_resp = client.post("/auth/login", json={"username":"admin", "password":"123456"})
    token = login_resp.get_json()["access_token"]
    resp = client.get("/api/data", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
