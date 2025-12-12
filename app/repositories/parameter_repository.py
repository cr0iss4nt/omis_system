from app.database import get_db_cursor


class ParameterRepository:
    @staticmethod
    def get(param_id):
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT id, experiment_id, name, value FROM experiment_parameters WHERE id=%s",
                (param_id,)
            )
            r = cur.fetchone()
            if not r:
                return None
            return dict(id=r[0], experiment_id=r[1], name=r[2], value=r[3])

    @staticmethod
    def get_by_experiment(exp_id):
        with get_db_cursor() as cur:
            cur.execute(
                "SELECT id, name, value FROM experiment_parameters WHERE experiment_id=%s ORDER BY id",
                (exp_id,)
            )
            rows = cur.fetchall()
            return [dict(id=row[0], name=row[1], value=row[2]) for row in rows]

    @staticmethod
    def add(exp_id, name, value):
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO experiment_parameters(experiment_id, name, value) VALUES (%s, %s, %s) RETURNING id",
                (exp_id, name, value)
            )
            return cur.fetchone()[0]

    @staticmethod
    def add_batch(exp_id, parameters):
        with get_db_cursor() as cur:
            for name, value in parameters.items():
                cur.execute(
                    "INSERT INTO experiment_parameters(experiment_id, name, value) VALUES (%s, %s, %s)",
                    (exp_id, name, str(value))
                )

    @staticmethod
    def update(param_id, name=None, value=None):
        with get_db_cursor() as cur:
            updates = []
            params = []

            if name:
                updates.append("name = %s")
                params.append(name)
            if value:
                updates.append("value = %s")
                params.append(value)

            if updates:
                params.append(param_id)
                cur.execute(
                    f"UPDATE experiment_parameters SET {', '.join(updates)} WHERE id = %s",
                    params
                )

    @staticmethod
    def delete(param_id):
        with get_db_cursor() as cur:
            cur.execute("DELETE FROM experiment_parameters WHERE id=%s", (param_id,))

    @staticmethod
    def delete_by_experiment(exp_id):
        with get_db_cursor() as cur:
            cur.execute("DELETE FROM experiment_parameters WHERE experiment_id=%s", (exp_id,))