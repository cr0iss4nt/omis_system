from app.repositories.lab_repository import LabRepository
from app.repositories.user_repository import UserRepository

class StudentService:
    @staticmethod
    def submit_lab(lab_id, student_id, value):
        LabRepository.submit_lab(lab_id, student_id, value)

    @staticmethod
    def get_my_labs(student_id):
        return LabRepository.get_student_labs(student_id)

    @staticmethod
    def get_lab_details(lab_id, student_id):
        labs = LabRepository.get_student_labs(student_id)
        for lab in labs:
            if lab['id'] == lab_id:
                return lab
        return None

    @staticmethod
    def get_profile(student_id):
        return UserRepository.get(student_id)