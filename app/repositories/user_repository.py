from app.database import get_db_cursor


class UserRepository:
    @staticmethod
    def get(user_id):
        with get_db_cursor() as cur:
            cur.execute("SELECT id, full_name, email, user_role FROM users WHERE id=%s", (user_id,))
            row = cur.fetchone()
            if not row:
                return None
            return dict(id=row[0], full_name=row[1], email=row[2], role=row[3])

    @staticmethod
    def get_by_email(email):
        with get_db_cursor() as cur:
            cur.execute("SELECT id, full_name, email, user_role FROM users WHERE email=%s", (email,))
            row = cur.fetchone()
            if not row:
                return None
            return dict(id=row[0], full_name=row[1], email=row[2], role=row[3])

    @staticmethod
    def get_all():
        with get_db_cursor() as cur:
            cur.execute("SELECT id, full_name, email, user_role FROM users ORDER BY id")
            rows = cur.fetchall()
            return [dict(id=row[0], full_name=row[1], email=row[2], role=row[3]) for row in rows]

    @staticmethod
    def add(full_name, email, role):
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO users(full_name, email, user_role) VALUES (%s, %s, %s) RETURNING id",
                (full_name, email, role)
            )
            return cur.fetchone()[0]

    @staticmethod
    def update(user_id, full_name=None, email=None, role=None):
        with get_db_cursor() as cur:
            updates = []
            params = []

            if full_name:
                updates.append("full_name = %s")
                params.append(full_name)
            if email:
                updates.append("email = %s")
                params.append(email)
            if role:
                updates.append("user_role = %s")
                params.append(role)

            if updates:
                params.append(user_id)
                cur.execute(
                    f"UPDATE users SET {', '.join(updates)} WHERE id = %s",
                    params
                )

    @staticmethod
    def delete(user_id):
        with get_db_cursor() as cur:
            cur.execute("DELETE FROM users WHERE id=%s", (user_id,))