import pytest
from flask import url_for
from flask_jwt_extended import create_access_token
from notice_service import app as flask_app, db


@pytest.fixture
@pytest.fixture
def app():
    """Flask 앱 픽스처"""
    flask_app.config['TESTING'] = True
    flask_app.config['SERVER_NAME'] = 'localhost.localdomain'
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    with flask_app.app_context():
        db.create_all()  # 데이터베이스 초기화
        yield flask_app
        db.session.remove()
        db.drop_all()  # 테스트 후 데이터베이스 삭제


@pytest.fixture
def client(app):
    """Flask 클라이언트 픽스처"""
    return app.test_client()


@pytest.fixture
def access_token():
    """Generate a valid JWT access token for testing."""
    with flask_app.app_context():
        return create_access_token(identity="test_user")


def test_unauthorized_access(client):
    """Test accesing a protected route without a JWT."""
    response = client.get(url_for('notice.some_protected_route'))
    assert response.status_code == 401
    assert "로그인이 필요한 서비스입니다." in response.data('utf-8')


def test_authorized_access(client, access_token):
    """Test accessing a protected route with a valid JWT."""
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = client.get(url_for('notice.some_protected_route'), headers=headers, follow_redirects=True)
    assert response.status_code == 200


def test_internal_error(client):
    """Test a scenario that triggers a 500 error."""
    response = client.get('/trigger_500')
    assert response.status_code == 500
    assert b"Internal Server Error" in response.data
