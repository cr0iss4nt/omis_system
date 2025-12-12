from app.database import get_db_cursor


class ModelRepository:
    @staticmethod
    def get(model_id):
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT m.id, m.name, m.description, m.model_type, m.file_id,
                       f.name as file_name, f.path as file_path
                FROM models m
                LEFT JOIN files f ON m.file_id = f.id
                WHERE m.id=%s
                """,
                (model_id,)
            )
            r = cur.fetchone()
            if not r:
                return None
            return dict(
                id=r[0], name=r[1], description=r[2], model_type=r[3],
                file_id=r[4], file_name=r[5], file_path=r[6]
            )

    @staticmethod
    def get_all():
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT m.id, m.name, m.description, m.model_type, m.file_id,
                       f.name as file_name
                FROM models m
                LEFT JOIN files f ON m.file_id = f.id
                ORDER BY m.id DESC
                """
            )
            rows = cur.fetchall()
            return [
                dict(
                    id=row[0], name=row[1], description=row[2],
                    model_type=row[3], file_id=row[4], file_name=row[5]
                ) for row in rows
            ]

    @staticmethod
    def add(name, description, model_type, file_id):
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO models(name, description, model_type, file_id) VALUES (%s, %s, %s, %s) RETURNING id",
                (name, description, model_type, file_id)
            )
            return cur.fetchone()[0]

    @staticmethod
    def update(model_id, name=None, description=None, model_type=None, file_id=None):
        with get_db_cursor() as cur:
            updates = []
            params = []

            if name:
                updates.append("name = %s")
                params.append(name)
            if description:
                updates.append("description = %s")
                params.append(description)
            if model_type:
                updates.append("model_type = %s")
                params.append(model_type)
            if file_id:
                updates.append("file_id = %s")
                params.append(file_id)

            if updates:
                params.append(model_id)
                cur.execute(
                    f"UPDATE models SET {', '.join(updates)} WHERE id = %s",
                    params
                )

    @staticmethod
    def delete(model_id):
        with get_db_cursor() as cur:
            cur.execute("DELETE FROM models WHERE id=%s", (model_id,))

    @staticmethod
    def get_by_type(model_type):
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT id, name FROM models WHERE model_type=%s ORDER BY name",
                (model_type,)
            )
            rows = cur.fetchall()
            return [dict(id=row[0], name=row[1]) for row in rows]