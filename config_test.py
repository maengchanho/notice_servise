import os
from config import Config
from dotenv import load_dotenv


def test_config(monkeypatch):
    load_dotenv()

    # 환경 변수 설정
    monkeypatch.setenv('DB_HOST', 'localhost')
    monkeypatch.setenv('DB_USER', 'root')
    monkeypatch.setenv('DB_PASSWORD', 'my-secret-pw')
    monkeypatch.setenv('JWT_SECRET_KEY', 'jwt_secret_key')
    monkeypatch.setenv('API_GATEWAY_SECRET_KEY', 'default-api-gateway-secret')

    # Config 클래스 인스턴스 생성
    config = Config()

    # 설정값 검증
    assert config.SECRET_KEY == 'default-api-gateway-secret', "API Gateway Secret Key should match"
    assert config.SQLALCHEMY_DATABASE_URI == 'mysql://root:my-secret-pw@localhost/notice_db', "Database URI should be constructed properly"
    assert not config.SQLALCHEMY_TRACK_MODIFICATIONS, "SQLAlchemy track modifications should be False"
    assert config.JWT_SECRET_KEY == 'jwt_secret_key', "JWT secret key should match"
    assert config.JWT_TOKEN_LOCATION == ['cookies'], "JWT token location should be 'cookies'"
    assert not config.JWT_COOKIE_SECURE, "JWT cookie secure should be False in this configuration"
    assert config.JWT_ACCESS_TOKEN_EXPIRES.total_seconds() == 3600, "JWT access token expiry should be 1 hour"
