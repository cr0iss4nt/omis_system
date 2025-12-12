from app.repositories.user_repository import UserRepository
from app.repositories.credentials_repository import CredentialsRepository


class AdminService:
    @staticmethod
    def get_all_users():
        users = UserRepository.get_all()
        for user in users:
            user['username'] = CredentialsRepository.get_by_user_id(user['id'])
        return users

    @staticmethod
    def create_user(full_name, email, username, password, role):
        if UserRepository.get_by_email(email):
            raise ValueError("User with this email already exists")
        if CredentialsRepository.username_exists(username):
            raise ValueError("Username already exists")

        user_id = UserRepository.add(full_name, email, role)
        CredentialsRepository.add(user_id, username, password)
        return user_id

    @staticmethod
    def update_user(user_id, full_name=None, email=None, role=None, password=None):
        if full_name or email or role:
            UserRepository.update(user_id, full_name, email, role)
        if password:
            CredentialsRepository.update_password(user_id, password)

    @staticmethod
    def delete_user(user_id):
        UserRepository.delete(user_id)

    @staticmethod
    def get_system_stats():
        from app.repositories.model_repository import ModelRepository
        from app.repositories.experiment_repository import ExperimentRepository

        with ModelRepository.get_all() as models, \
                ExperimentRepository.get_all() as experiments, \
                UserRepository.get_all() as users:

            stats = {
                'total_users': len(users),
                'total_models': len(models),
                'total_experiments': len(experiments),
                'users_by_role': {},
                'models_by_type': {}
            }

            for user in users:
                role = user['role']
                stats['users_by_role'][role] = stats['users_by_role'].get(role, 0) + 1

            for model in models:
                model_type = model['model_type']
                stats['models_by_type'][model_type] = stats['models_by_type'].get(model_type, 0) + 1

            return stats