import hashlib
from passlib.hash import bcrypt
from app.database import get_db_cursor


class CredentialsRepository:
    @staticmethod
    def add(user_id, username, password):
        hashed = bcrypt.hash(hashlib.sha256(password.encode()).hexdigest())
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO credentials(id, username, pass) VALUES (%s, %s, %s)",
                (user_id, username, hashed)
            )

    @staticmethod
    def auth(username, password):
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT id, pass FROM credentials WHERE username=%s",
                (username,)
            )
            row = cur.fetchone()
            if not row:
                return None

            user_id, stored_hash = row

            password_sha256 = hashlib.sha256(password.encode()).hexdigest()
            if bcrypt.verify(password_sha256, stored_hash):
                return user_id

            return None

    @staticmethod
    def get_by_user_id(user_id):
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT username FROM credentials WHERE id=%s",
                (user_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None

    @staticmethod
    def update_password(user_id, new_password):
        password_sha256 = hashlib.sha256(new_password.encode()).hexdigest()
        hashed = bcrypt.hash(password_sha256)
        with get_db_cursor() as cur:
            cur.execute(
                "UPDATE credentials SET pass=%s WHERE id=%s",
                (hashed, user_id)
            )

    @staticmethod
    def username_exists(username):
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT 1 FROM credentials WHERE username=%s",
                (username,)
            )
            return cur.fetchone() is not None