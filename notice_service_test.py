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
def access_token(client):
    with client.application.app_context():
        from flask_jwt_extended import create_access_token
        return create_access_token(identity="test_user")


def test_notice_login_redirect(client):
    response = client.get('notice.some_protected_route')
    assert response.status_code == 401
    error_message = response.get_json()["error"]
    assert "로그인이 필요한 서비스입니다." in error_message


def test_authorized_access(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get('notice.some_protected_route', headers=headers)
    assert response.status_code == 200


def test_internal_error(client):
    response = client.get('/trigger_401')
    assert response.status_code == 401
