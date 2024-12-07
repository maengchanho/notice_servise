import os
from datetime import timedelta
import pytest
from config import Config
from dotenv import load_dotenv


load_dotenv()


@pytest.fixture
def set_env_vars():
    # 환경 변수를 설정하는 fixture.
    os.environ['NOTICE_SERVICE_SECRET_KEY'] = 'notice_service_secret_key'
    os.environ['DB_USER'] = 'root'
    os.environ['DB_PASSWORD'] = 'my-secret-pw'
    os.environ['DB_HOST'] = 'localhost'
    os.environ['JWT_SECRET_KEY'] = 'jwt_secret_key'
    yield
    # 테스트 후 환경 변수 제거
    del os.environ['NOTICE_SERVICE_SECRET_KEY']
    del os.environ['DB_USER']
    del os.environ['DB_PASSWORD']
    del os.environ['DB_HOST']
    del os.environ['JWT_SECRET_KEY']


def test_config_values(set_env_vars):
    # Config 클래스가 환경 변수를 올바르게 로드하는지 테스트
    config = Config()

    assert config.SECRET_KEY == 'notice_service_secret_key'
    assert config.SQLALCHEMY_DATABASE_URI == 'mysql://root:my-secret-pw@localhost/notice_db'
    assert config.SQLALCHEMY_TRACK_MODIFICATIONS is False
    assert config.JWT_SECRET_KEY == 'jwt_secret_key'
    assert config.JWT_TOKEN_LOCATION == ['cookies']
    assert config.JWT_COOKIE_SECURE is False
    assert config.JWT_ACCESS_TOKEN_EXPIRES == timedelta(hours=1)


def test_default_values():
    # 환경 변수가 설정되지 않았을 때 기본값을 테스트.
    config = Config()

    assert config.SECRET_KEY == 'default-api-gateway-secret'
    assert config.JWT_SECRET_KEY == 'jwt_secret_key'
    assert config.JWT_TOKEN_LOCATION == ['cookies']
    assert config.JWT_COOKIE_SECURE is False
    assert config.JWT_ACCESS_TOKEN_EXPIRES == timedelta(hours=1)