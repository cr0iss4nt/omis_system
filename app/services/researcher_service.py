from app.repositories.experiment_repository import ExperimentRepository
from app.repositories.model_repository import ModelRepository
from app.repositories.parameter_repository import ParameterRepository

class ResearcherService:
    @staticmethod
    def create_experiment(name, description, model_id, parameters=None):
        exp_id = ExperimentRepository.add(name, description, model_id)
        if parameters:
            ParameterRepository.add_batch(exp_id, parameters)
        return exp_id

    @staticmethod
    def get_experiments():
        return ExperimentRepository.get_all()

    @staticmethod
    def get_experiment(exp_id):
        experiment = ExperimentRepository.get(exp_id)
        if experiment:
            experiment['parameters'] = ParameterRepository.get_by_experiment(exp_id)
        return experiment

    @staticmethod
    def create_model(name, description, model_type, file_id):
        return ModelRepository.add(name, description, model_type, file_id)

    @staticmethod
    def get_models():
        return ModelRepository.get_all()

    @staticmethod
    def get_model(model_id):
        return ModelRepository.get(model_id)