import os
import pytest
from datetime import timedelta
from config import Config
from dotenv import load_dotenv


@pytest.fixture
def set_env_vars(monkeypatch):
    """.env 파일에서 환경 변수를 로드하고 덮어쓰기"""
    load_dotenv()  # .env 파일 로드
    monkeypatch.setenv('API_GATEWAY_SECRET_KEY', os.getenv('NOTICE_SERVICE_SECRET_KEY', 'default-api-gateway-secret'))
    monkeypatch.setenv('DB_USER', os.getenv('DB_USER', 'root'))
    monkeypatch.setenv('DB_PASSWORD', os.getenv('DB_PASSWORD', 'my-secret-pw'))
    monkeypatch.setenv('DB_HOST', os.getenv('DB_HOST', 'localhost'))
    monkeypatch.setenv('JWT_SECRET_KEY', os.getenv('JWT_SECRET_KEY', 'jwt_secret_key'))
    yield


def test_config_values(set_env_vars):
    # Config 클래스의 설정값을 검증하는 테스트
    config = Config()

    # 환경 변수 기반으로 설정된 값 확인
    assert config.SQLALCHEMY_DATABASE_URI == "mysql://root:my-secret-pw@localhost/notice_db"
    assert config.SECRET_KEY == 'notice_service_secret_key'
    assert config.JWT_SECRET_KEY == 'jwt_secret_key'

    # 기본 설정값 확인
    assert config.SQLALCHEMY_TRACK_MODIFICATIONS is False
    assert config.JWT_TOKEN_LOCATION == ['cookies']
    assert config.JWT_COOKIE_SECURE is False
    assert config.JWT_ACCESS_TOKEN_EXPIRES == timedelta(hours=1)


def test_default_values_when_env_vars_missing(monkeypatch):
    # 환경 변수가 없을 때 기본값을 사용하는지 검증

    # 모든 환경 변수를 제거
    monkeypatch.delenv('DB_USER', raising=False)
    monkeypatch.delenv('DB_PASSWORD', raising=False)
    monkeypatch.delenv('DB_HOST', raising=False)
    monkeypatch.delenv('JWT_SECRET_KEY', raising=False)
    monkeypatch.delenv('NOTICE_SERVICE_SECRET_KEY', raising=False)

    config = Config()

    # 기본값 확인
    assert config.SQLALCHEMY_DATABASE_URI == "mysql://None:None@None/notice_db"
    assert config.SECRET_KEY == 'default-api-gateway-secret'
    assert config.JWT_SECRET_KEY == 'default-jwt-secret'
    assert config.SQLALCHEMY_TRACK_MODIFICATIONS is False
    assert config.JWT_TOKEN_LOCATION == ['cookies']
    assert config.JWT_COOKIE_SECURE is False
    assert config.JWT_ACCESS_TOKEN_EXPIRES == timedelta(hours=1)