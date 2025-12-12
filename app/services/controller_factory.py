from app.services.researcher_service import ResearcherService
from app.services.teacher_service import TeacherService
from app.services.student_service import StudentService
from app.services.admin_service import AdminService

class ControllerFactory:
    @staticmethod
    def get(role):
        if role == "teacher":
            return TeacherService()
        if role == "researcher":
            return ResearcherService()
        if role == "student":
            return StudentService()
        if role == "admin":
            return AdminService()
        return None

    @staticmethod
    def get_for_user(user):
        if user and 'role' in user:
            return ControllerFactory.get(user['role'])
        return None