from app.database import get_db_cursor


class ExperimentRepository:
    @staticmethod
    def get(exp_id):
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT e.id, e.name, e.description, e.model_id,
                       m.name as model_name
                FROM experiments e
                LEFT JOIN models m ON e.model_id = m.id
                WHERE e.id=%s
                """,
                (exp_id,)
            )
            r = cur.fetchone()
            if not r:
                return None
            return dict(
                id=r[0], name=r[1], description=r[2],
                model_id=r[3], model_name=r[4]
            )

    @staticmethod
    def get_all():
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT e.id, e.name, e.description, e.model_id,
                       m.name as model_name, COUNT(p.id) as param_count
                FROM experiments e
                LEFT JOIN models m ON e.model_id = m.id
                LEFT JOIN experiment_parameters p ON e.id = p.experiment_id
                GROUP BY e.id, e.name, e.description, e.model_id, m.name
                ORDER BY e.id DESC
                """
            )
            rows = cur.fetchall()
            return [
                dict(
                    id=row[0], name=row[1], description=row[2],
                    model_id=row[3], model_name=row[4], param_count=row[5]
                ) for row in rows
            ]

    @staticmethod
    def add(name, description, model_id):
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO experiments(name, description, model_id) VALUES (%s, %s, %s) RETURNING id",
                (name, description, model_id)
            )
            return cur.fetchone()[0]

    @staticmethod
    def update(exp_id, name=None, description=None, model_id=None):
        with get_db_cursor() as cur:
            updates = []
            params = []

            if name:
                updates.append("name = %s")
                params.append(name)
            if description:
                updates.append("description = %s")
                params.append(description)
            if model_id:
                updates.append("model_id = %s")
                params.append(model_id)

            if updates:
                params.append(exp_id)
                cur.execute(
                    f"UPDATE experiments SET {', '.join(updates)} WHERE id = %s",
                    params
                )

    @staticmethod
    def delete(exp_id):
        with get_db_cursor() as cur:
            cur.execute("DELETE FROM experiments WHERE id=%s", (exp_id,))

    @staticmethod
    def get_by_model(model_id):
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT id, name FROM experiments WHERE model_id=%s ORDER BY id DESC",
                (model_id,)
            )
            rows = cur.fetchall()
            return [dict(id=row[0], name=row[1]) for row in rows]