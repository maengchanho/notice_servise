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


def test_notice_pagination(client, db_session):
    # 테스트 데이터 여러 개 추가
    for i in range(15):
        notice = Notice(title=f"Notice {i+1}", content=f"Content {i+1}")
        db_session.add(notice)
    db_session.commit()
    
    # 페이지네이션 테스트 - 첫 번쨰 페이지
    response = client.get('/notice?page=1&per_page=5')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['notice']) = 5 # 5개의 공지사항이 반환
    assert data['notice'][0]['title'] == "Notice 1"
    
    # 페이지네이션 테스트 - 두 번쨰 페이지
    response = client.get('/notice?page=1&per_page=5')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['notice']) = 5 # 5개의 공지사항이 반환
    assert data['notice'][0]['title'] == "Notice 6"
    
    # 페이지네이션 테스트 - 세 번쨰 페이지
    response = client.get('/notice?page=1&per_page=5')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['notice']) = 5 # 5개의 공지사항이 반환
    assert data['notice'][0]['title'] == "Notice 11"
    
    # 페이지네이션 테스트 - 페이지 벗어난 경우
    response = client.get('/notice?page=1&per_page=5')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['notice']) == 0 # 더 이상 데이터가 없을 경우 빈 리스트 반환
    

def test_notice_detail(client, db_session):
    # 테스트 데이터 추가
    notice = Notice(titile="Detail Test", content="Detail Content")
    db_session.add(notice)
    db_session.commit()
    
    # 방금 추가된 공지사항 ID 확인
    notice_id = notice.id
    
    # 상세 정보 요청
    response = client.get(f'/notices/{notice_id}')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['title'] == "Detail Test"
    assert data['content'] == "Detail Content"


def test_pagination_navigation(client, db_session):
    # 테스트 데이터 여러 개 추가
    for i in range(12):
        notice = Notice(title=f"Page Test {i+1}", content=f"Page Content {i+1}")
        db_session.add(notice)
    db_session.commit()

    # 첫 번째 페이지 요청
    response = client.get('/notices?page=1&per_page=5')
    assert response.status_code == 200
    data = response.get_json()
    assert data['has_next'] is True  # 다음 페이지 존재
    assert data['has_prev'] is False  # 이전 페이지 없음

    # 두 번째 페이지 요청
    response = client.get('/notices?page=2&per_page=5')
    assert response.status_code == 200
    data = response.get_json()
    assert data['has_next'] is True
    assert data['has_prev'] is True

    # 마지막 페이지 요청
    response = client.get('/notices?page=3&per_page=5')
    assert response.status_code == 200
    data = response.get_json()
    assert data['has_next'] is False  # 다음 페이지 없음
    assert data['has_prev'] is True   # 이전 페이지 존재
