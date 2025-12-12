from app.database import get_db_cursor

class FileRepository:
    @staticmethod
    def get(file_id):
        with get_db_cursor() as cur:
            cur.execute("SELECT id, name, path FROM files WHERE id=%s", (file_id,))
            r = cur.fetchone()
            if not r:
                return None
            return dict(id=r[0], name=r[1], path=r[2])

    @staticmethod
    def get_all():
        with get_db_cursor() as cur:
            cur.execute("SELECT id, name, path FROM files ORDER BY id DESC")
            rows = cur.fetchall()
            return [dict(id=row[0], name=row[1], path=row[2]) for row in rows]

    @staticmethod
    def add(name, path):
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO files(name, path) VALUES (%s, %s) RETURNING id",
                (name, path)
            )
            return cur.fetchone()[0]

    @staticmethod
    def delete(file_id):
        with get_db_cursor() as cur:
            cur.execute("DELETE FROM files WHERE id=%s", (file_id,))

    @staticmethod
    def get_by_model(model_id):
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT f.id, f.name, f.path 
                FROM files f 
                JOIN models m ON f.id = m.file_id 
                WHERE m.id = %s
                """,
                (model_id,)
            )
            r = cur.fetchone()
            if not r:
                return None
            return dict(id=r[0], name=r[1], path=r[2])