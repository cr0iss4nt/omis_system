from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
import json
from app.auth import get_current_user
from app.repositories.model_repository import ModelRepository
from app.repositories.experiment_repository import ExperimentRepository
from app.repositories.parameter_repository import ParameterRepository
from app.services.researcher_service import ResearcherService
#from app.templates import templates
from app.templates_loader import templates

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("/", response_class=HTMLResponse)
async def list_experiments(
        request: Request,
        user=Depends(get_current_user),
        page: int = Query(1, ge=1),
        model_id: int = Query(None)
):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    if model_id:
        experiments = ExperimentRepository.get_by_model(model_id)
    else:
        experiments = ResearcherService.get_experiments()

    models = ModelRepository.get_all()

    return templates.TemplateResponse(
        "experiments/list.html",
        {
            "request": request,
            "user": user,
            "experiments": experiments,
            "models": models,
            "page": page,
            "selected_model_id": model_id
        }
    )


@router.get("/create", response_class=HTMLResponse)
async def create_experiment_page(request: Request, user=Depends(get_current_user)):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    models = ModelRepository.get_all()

    return templates.TemplateResponse(
        "experiments/create.html",
        {
            "request": request,
            "user": user,
            "models": models
        }
    )


@router.post("/create")
async def create_experiment(
        request: Request,
        name: str = Form(...),
        description: str = Form(...),
        model_id: int = Form(...),
        parameters_json: str = Form("{}"),
        user=Depends(get_current_user)
):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    try:
        parameters = json.loads(parameters_json)

        experiment_id = ResearcherService.create_experiment(
            name, description, model_id, parameters
        )

        return RedirectResponse(url=f"/experiments/{experiment_id}", status_code=302)
    except json.JSONDecodeError:
        models = ModelRepository.get_all()
        return templates.TemplateResponse(
            "experiments/create.html",
            {
                "request": request,
                "user": user,
                "models": models,
                "error": "Invalid JSON in parameters"
            }
        )
    except Exception as e:
        models = ModelRepository.get_all()
        return templates.TemplateResponse(
            "experiments/create.html",
            {
                "request": request,
                "user": user,
                "models": models,
                "error": str(e)
            }
        )


@router.get("/{experiment_id}", response_class=HTMLResponse)
async def experiment_detail(request: Request, experiment_id: int, user=Depends(get_current_user)):
    experiment = ResearcherService.get_experiment(experiment_id)
    if not experiment:
        return RedirectResponse(url="/experiments")

    return templates.TemplateResponse(
        "experiments/detail.html",
        {
            "request": request,
            "user": user,
            "experiment": experiment
        }
    )


@router.get("/{experiment_id}/edit", response_class=HTMLResponse)
async def edit_experiment_page(request: Request, experiment_id: int, user=Depends(get_current_user)):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    experiment = ExperimentRepository.get(experiment_id)
    if not experiment:
        return RedirectResponse(url="/experiments")

    models = ModelRepository.get_all()
    parameters = ParameterRepository.get_by_experiment(experiment_id)

    return templates.TemplateResponse(
        "experiments/edit.html",
        {
            "request": request,
            "user": user,
            "experiment": experiment,
            "models": models,
            "parameters": parameters
        }
    )


@router.post("/{experiment_id}/update")
async def update_experiment(
        request: Request,
        experiment_id: int,
        name: str = Form(None),
        description: str = Form(None),
        model_id: int = Form(None),
        user=Depends(get_current_user)
):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    ExperimentRepository.update(experiment_id, name, description, model_id)
    return RedirectResponse(url=f"/experiments/{experiment_id}", status_code=302)


@router.post("/{experiment_id}/add-parameter")
async def add_parameter(
        request: Request,
        experiment_id: int,
        param_name: str = Form(...),
        param_value: str = Form(...),
        user=Depends(get_current_user)
):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    ParameterRepository.add(experiment_id, param_name, param_value)
    return RedirectResponse(url=f"/experiments/{experiment_id}", status_code=302)


@router.post("/{experiment_id}/delete-parameter/{param_id}")
async def delete_parameter(
        request: Request,
        experiment_id: int,
        param_id: int,
        user=Depends(get_current_user)
):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    ParameterRepository.delete(param_id)
    return RedirectResponse(url=f"/experiments/{experiment_id}", status_code=302)


@router.post("/{experiment_id}/delete")
async def delete_experiment(
        request: Request,
        experiment_id: int,
        user=Depends(get_current_user)
):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    ExperimentRepository.delete(experiment_id)
    return RedirectResponse(url="/experiments", status_code=302)