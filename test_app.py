import os
import tempfile
import unittest
import sqlite3
from werkzeug.security import generate_password_hash
import app as app_module

class EventSystemTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        app_module.DB_PATH = self.tmp.name
        app_module.app.config.update(TESTING=True, SECRET_KEY="test-secret")
        app_module.init_db()
        self.client = app_module.app.test_client()
        with app_module.app.app_context():
            db = app_module.get_db()
            self.user_id = db.execute(
                "INSERT INTO users(full_name,email,password_hash) VALUES(?,?,?)",
                ("Test User", "test@example.com", generate_password_hash("TestPass123"))
            ).lastrowid
            self.category_id = db.execute("SELECT id FROM categories LIMIT 1").fetchone()[0]
            self.event_id = db.execute(
                """INSERT INTO events(title,description,category_id,event_date,event_time,location,capacity)
                   VALUES(?,?,?,?,?,?,?)""",
                ("Test Event", "Test description", self.category_id, "2099-05-20", "12:00", "Room 1", 1)
            ).lastrowid
            db.commit()

    def tearDown(self):
        try:
            os.unlink(self.tmp.name)
        except OSError:
            pass

    def login_user(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = self.user_id
            sess["full_name"] = "Test User"
            sess["role"] = "user"

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Event", response.data)

    def test_search_by_title(self):
        response = self.client.get("/?q=Test%20Event")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Test Event", response.data)
        response = self.client.get("/?q=not-found")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Uyğun tədbir tapılmadı".encode(), response.data)

    def test_registration_requires_login(self):
        response = self.client.post(f"/event/{self.event_id}/join", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("əvvəlcə sistemə daxil olun".encode(), response.data)

    def test_user_can_register_once(self):
        self.login_user()
        response = self.client.post(f"/event/{self.event_id}/join", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        with app_module.app.app_context():
            count = app_module.get_db().execute(
                "SELECT COUNT(*) FROM registrations WHERE user_id=? AND event_id=?",
                (self.user_id, self.event_id)
            ).fetchone()[0]
            self.assertEqual(count, 1)
        self.client.post(f"/event/{self.event_id}/join", follow_redirects=True)
        with app_module.app.app_context():
            count = app_module.get_db().execute(
                "SELECT COUNT(*) FROM registrations WHERE user_id=? AND event_id=?",
                (self.user_id, self.event_id)
            ).fetchone()[0]
            self.assertEqual(count, 1)

    def test_capacity_limit_blocks_second_user(self):
        self.login_user()
        self.client.post(f"/event/{self.event_id}/join")
        with app_module.app.app_context():
            db = app_module.get_db()
            second_id = db.execute(
                "INSERT INTO users(full_name,email,password_hash) VALUES(?,?,?)",
                ("Second User", "second@example.com", generate_password_hash("SecondPass123"))
            ).lastrowid
            db.commit()
        with self.client.session_transaction() as sess:
            sess["user_id"] = second_id
            sess["full_name"] = "Second User"
            sess["role"] = "user"
        response = self.client.post(f"/event/{self.event_id}/join", follow_redirects=True)
        self.assertIn("bütün yerlər dolub".encode(), response.data)
        with app_module.app.app_context():
            count = app_module.get_db().execute(
                "SELECT COUNT(*) FROM registrations WHERE event_id=?", (self.event_id,)
            ).fetchone()[0]
            self.assertEqual(count, 1)

    def test_admin_page_requires_admin(self):
        response = self.client.get("/admin", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("yalnız administrator".encode(), response.data)

if __name__ == "__main__":
    unittest.main()
