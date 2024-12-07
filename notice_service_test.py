import pytest
from notice_service import app, db
from flask_jwt_extended import create_access_token


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


@pytest.fixture
def access_token():
    return create_access_token(identity="test_user")


def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200


def test_protected_endpoint_without_jwt(client):
    response = client.get('/protected-endpoint')
    assert response.status_code == 401


def test_protected_endpoint_with_jwt(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get('/protected-endpoint', headers=headers)
    assert response.status_code == 200


def test_notice_login_redirect(client):
    response = client.get('/notice/protected-page')
    assert response.status_code == 401
    assert "로그인이 필요한 서비스입니다." in response.get_json()["error"]
