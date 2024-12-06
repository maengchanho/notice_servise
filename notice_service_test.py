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


def test_unauthorized_access_returns_401(client):
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    response = client.get('/', headers=headers)
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    json_data = response.get_json()
    assert json_data is not None, "Expected a JSON response."
    assert "error" in json_data, "Expected 'error' key in the JSON response."
    assert "로그인이 필요한 서비스입니다." in json_data["error"], "Expected the error message in the response"


def test_authorized_access(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get('/', headers=headers)
    assert response.status_code == 200


def test_internal_error(client):
    response = client.get('/api/notices')
