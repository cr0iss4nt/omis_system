from datetime import datetime
from app.repositories.lab_repository import LabRepository
from app.repositories.user_repository import UserRepository

class TeacherService:
    @staticmethod
    def create_lab(name, instruction, deadline, experiment_id):
        if isinstance(deadline, str):
            deadline = datetime.fromisoformat(deadline)
        return LabRepository.add(name, instruction, deadline, experiment_id)

    @staticmethod
    def get_labs():
        return LabRepository.get_all()

    @staticmethod
    def get_lab(lab_id):
        lab = LabRepository.get(lab_id)
        if lab:
            lab['assignments'] = LabRepository.get_assignments(lab_id)
        return lab

    @staticmethod
    def assign_lab(lab_id, student_id):
        LabRepository.assign(lab_id, student_id)

    @staticmethod
    def assign_lab_to_multiple(lab_id, student_ids):
        for student_id in student_ids:
            LabRepository.assign(lab_id, student_id)

    @staticmethod
    def grade_lab(lab_id, student_id, grade):
        LabRepository.grade(lab_id, student_id, grade)

    @staticmethod
    def get_students():
        return [user for user in UserRepository.get_all() if user['role'] == 'student']

    @staticmethod
    def get_lab_submissions(lab_id):
        return LabRepository.get_assignments(lab_id)