from datetime import datetime
from app.database import get_db_cursor


class LabRepository:
    @staticmethod
    def get(lab_id):
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT l.id, l.name, l.instruction, l.deadline, l.id,
                       e.name as experiment_name
                FROM labs l
                LEFT JOIN experiments e ON l.id = e.id
                WHERE l.id=%s
                """,
                (lab_id,)
            )
            r = cur.fetchone()
            if not r:
                return None
            return dict(
                id=r[0], name=r[1], instruction=r[2],
                deadline=r[3], experiment_id=r[4], experiment_name=r[5]
            )

    @staticmethod
    def get_all():
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT l.id, l.name, l.instruction, l.deadline, l.id,
                       e.name as experiment_name,
                       COUNT(DISTINCT al.student_id) as assigned_count,
                       COUNT(DISTINCT lr.student_id) as submitted_count
                FROM labs l
                LEFT JOIN experiments e ON l.id = e.id
                LEFT JOIN assigned_labs al ON l.id = al.lab_id
                LEFT JOIN lab_results lr ON l.id = lr.lab_id
                GROUP BY l.id, l.name, l.instruction, l.deadline, l.id, e.name
                ORDER BY l.deadline DESC
                """
            )
            rows = cur.fetchall()
            return [
                dict(
                    id=row[0], name=row[1], instruction=row[2], deadline=row[3],
                    experiment_id=row[4], experiment_name=row[5],
                    assigned_count=row[6], submitted_count=row[7]
                ) for row in rows
            ]

    @staticmethod
    def add(name, instruction, deadline, experiment_id):
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO labs(name, instruction, deadline, id) VALUES (%s, %s, %s, %s) RETURNING id",
                (name, instruction, deadline, experiment_id)
            )
            return cur.fetchone()[0]

    @staticmethod
    def update(lab_id, name=None, instruction=None, deadline=None, experiment_id=None):
        with get_db_cursor() as cur:
            updates = []
            params = []

            if name:
                updates.append("name = %s")
                params.append(name)
            if instruction:
                updates.append("instruction = %s")
                params.append(instruction)
            if deadline:
                updates.append("deadline = %s")
                params.append(deadline)
            if experiment_id:
                updates.append("id = %s")
                params.append(experiment_id)

            if updates:
                params.append(lab_id)
                cur.execute(
                    f"UPDATE labs SET {', '.join(updates)} WHERE id = %s",
                    params
                )

    @staticmethod
    def delete(lab_id):
        with get_db_cursor() as cur:
            cur.execute("DELETE FROM labs WHERE id=%s", (lab_id,))

    @staticmethod
    def assign(lab_id, student_id):
        with get_db_cursor() as cur:
            cur.execute(
                "INSERT INTO assigned_labs(lab_id, student_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                (lab_id, student_id)
            )

    @staticmethod
    def grade(lab_id, student_id, grade):
        with get_db_cursor() as cur:
            cur.execute(
                "UPDATE assigned_labs SET grade=%s WHERE lab_id=%s AND student_id=%s",
                (grade, lab_id, student_id)
            )

    @staticmethod
    def get_assignments(lab_id):
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT al.student_id, u.full_name, u.email, al.grade
                FROM assigned_labs al
                JOIN users u ON al.student_id = u.id
                WHERE al.lab_id = %s
                ORDER BY u.full_name
                """,
                (lab_id,)
            )
            rows = cur.fetchall()
            return [
                dict(student_id=row[0], full_name=row[1], email=row[2], grade=row[3])
                for row in rows
            ]

    @staticmethod
    def get_student_labs(student_id):
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT l.id, l.name, l.instruction, l.deadline, al.grade,
                       lr.value as submission, lr.submitted_at
                FROM assigned_labs al
                JOIN labs l ON al.lab_id = l.id
                LEFT JOIN lab_results lr ON l.id = lr.lab_id AND lr.student_id = al.student_id
                WHERE al.student_id = %s
                ORDER BY l.deadline
                """,
                (student_id,)
            )
            rows = cur.fetchall()
            return [
                dict(
                    id=row[0], name=row[1], instruction=row[2], deadline=row[3],
                    grade=row[4], submission=row[5], submitted_at=row[6]
                ) for row in rows
            ]

    @staticmethod
    def submit_lab(lab_id, student_id, value):
        with get_db_cursor() as cur:
            cur.execute(
                """
                INSERT INTO lab_results(lab_id, student_id, value, submitted_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (lab_id, student_id) 
                DO UPDATE SET value = EXCLUDED.value, submitted_at = EXCLUDED.submitted_at
                """,
                (lab_id, student_id, value, datetime.utcnow())
            )