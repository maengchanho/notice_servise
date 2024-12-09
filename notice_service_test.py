import unittest
import os
import time
from flask import url_for
from notice_service import app, db
from models import Notice
from datetime import date
import json
from sqlalchemy.exc import OperationalError

class TestNoticeService(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{os.getenv('DB_USER', 'root')}:{os.getenv('DB_PASSWORD', 'mysql')}@{os.getenv('DB_HOST', 'mysql')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'notice_db')}"
        self.app = app.test_client()
        
        self._wait_for_mysql()
        
    def _wait_for_mysql(self):
        retries = 30
        while retries > 0:
            try:
                with app.app_context():
                    db.engine.connect()
                return
            except OperationalError:
                retries -= 1
                time.sleep(2)
        raise Exception("MySQL not available after retries")
    
    def test_home_redirect(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/news' in response.location)
    
    def test_news_page(self):
        response = self.app.get('/news')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'University Notices', response.data)
    
    def test_news_item(self):
        with app.app_context():
            notice = Notice(title='Test Notice', content='Test Content', date=date.today())
            db.session.add(notice)
            db.session.commit()
    
            response = self.app.get(f'/news/{notice.id}')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test Notice', response.data)
            self.assertIn(b'Test Content', response.data)
    
    def test_api_notices(self):
        with app.app_context():
            notice1 = Notice(title='Notice 1', content='Content 1', date=date.today())
            notice2 = Notice(title='Notice 2', content='Content 2', date=date.today())
            db.session.add(notice1)
            db.session.add(notice2)
            db.session.commit()
            
            response = self.app.get('/api/notices')
            self.assertCountEqual(response.status_code, 200)
            data = json.loads(response.data)
            
            self.assertCountEqual(len(data), 7)
            
            self.assertEqual(data[0]['title'], 'Holiday Announcement')
            self.assertEqual(data[1]['title'], 'Notice 1')
            self.assertEqual(data[2]['title'], 'Notice 2')
