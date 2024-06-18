import unittest
import psycopg2
import hashlib

DB_NAME = "NewBD1"
DB_USER = "postgres"
DB_PASSWORD = "123"
DB_HOST = "localhost"
DB_PORT = "5432"

def connect_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, password):
    conn = connect_db()
    cur = conn.cursor()
    try:
        password_hash = hash_password(password)
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def login(username, password):
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        return user and user[1] == hash_password(password)
    finally:
        cur.close()
        conn.close()

def load_messages():
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM messages")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def save_messages(messages):
    conn = connect_db()
    cur = conn.cursor()
    try:
        for message in messages:
            cur.execute("INSERT INTO messages (user_id, message) VALUES (%s, %s)", (message['user_id'], message['message']))
        conn.commit()
    finally:
        cur.close()
        conn.close()

class TestUserFunctions(unittest.TestCase):
    def setUp(self):
        self.conn = connect_db()
        self.cur = self.conn.cursor()
        self.cur.execute("DELETE FROM messages")
        self.cur.execute("DELETE FROM users")
        self.conn.commit()

    def tearDown(self):
        self.cur.close()
        self.conn.close()

    def test_hash_password(self):
        password = "testpassword"
        hashed = hash_password(password)
        self.assertEqual(hashed, hashlib.sha256(password.encode()).hexdigest())

    def test_register(self):
        username = "testuser"
        password = "testpassword"
        register(username, password)
        self.cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = self.cur.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user[1], username)
        self.assertEqual(user[2], hash_password(password))

    def test_login_success(self):
        username = "testuser"
        password = "testpassword"
        register(username, password)
        self.assertTrue(login(username, password))

    def test_login_fail_wrong_password(self):
        username = "testuser"
        password = "testpassword"
        register(username, password)
        self.assertFalse(login(username, "wrongpassword"))

    def test_login_fail_no_user(self):
        self.assertFalse(login("nouser", "password"))

    def test_chat_message(self):
        username = "testuser"
        password = "testpassword"
        register(username, password)
        self.cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = self.cur.fetchone()[0]
        message = "Hello, world!"
        save_messages([{'user_id': user_id, 'message': message}])
        messages = load_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0][1], user_id)
        self.assertEqual(messages[0][2], message)

if __name__ == '__main__':
    unittest.main()

