import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from models import db, Notice


@pytest.fixture
def app():
    # Flask 애플리케이션 테스트 설정
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    # Flask 테스트 클라이언트 설정
    return app.test_client()


@pytest.fixture
def db_session(app):
    # 데이터베이스 세션 설정
    with app.app_context():
        yield db.session


def test_create_notice(db_session):
    notice = Notice(title="Test Title", content="Test Content")
    db_session.add(notice)
    db_session.commit()
    # 데이터베이스에서 방금 저장한 데이터 확인
    saved_notice = Notice.query.first()
    assert saved_notice is not None
    assert saved_notice.title == "Test Title"
    assert saved_notice.content == "Test Content"
    assert saved_notice.date == date.today()


def test_query_notice(db_session):
    # 테스트 데이터를 추가
    notice = Notice(title="Query Test", content="Query Content")
    db_session.add(notice)
    db_session.commit()
    # 데이터 조회
    queried_notice = Notice.query.filter_by(title="Query Test").first()
    assert queried_notice is not None
    assert queried_notice.content == "Query Content"


def test_update_notice(db_session):
    notice = Notice(title="Update Test", content="Qriginal Content")
    db_session.add(notice)
    db_session.commit()
    # 데이터 업데이트
    notice_to_update = Notice.query.filter_by(title="Update Test").first()
    notice_to_update.content = "Updated Content"
    db_session.commit()
    # 업데이트 된 데이터 확인
    updated_notice = Notice.query.filter_by(title="Update Test").first()
    assert updated_notice.content == "Updated Content"


def test_delete_notice(db_session):
    # 데이터 추가
    notice = Notice(title="Delete Test", content="Delete Content")
    db_session.add(notice)
    db_session.commit()
    # 데이터 삭제
    notice_to_delete = Notice.query.filter_by(title="Delete Test").first()
    db_session.delete(notice_to_delete)
    db_session.commit()
    # 데이터가 삭제되었는지 확인
    deleted_notice = Notice.query.filter_by(title="Delete Test").first()
    assert deleted_notice is None