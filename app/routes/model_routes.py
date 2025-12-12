from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, Query
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import uuid
from app.auth import get_current_user
from app.repositories.model_repository import ModelRepository
from app.repositories.file_repository import FileRepository
from app.services.researcher_service import ResearcherService
from app.config import Config
from app.templates_loader import templates

router = APIRouter(prefix="/models", tags=["models"])


@router.get("/", response_class=HTMLResponse)
async def list_models(
        request: Request,
        user=Depends(get_current_user),
        page: int = Query(1, ge=1),
        model_type: str = Query(None)
):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    if model_type:
        models = ModelRepository.get_by_type(model_type)
    else:
        models = ModelRepository.get_all()

    return templates.TemplateResponse(
        "models/list.html",
        {
            "request": request,
            "user": user,
            "models": models,
            "page": page,
            "model_type": model_type,
            "model_types": ["classification", "regression", "clustering", "neural_network", "other"]
        }
    )


@router.get("/create", response_class=HTMLResponse)
async def create_model_page(request: Request, user=Depends(get_current_user)):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    return templates.TemplateResponse(
        "models/create.html",
        {
            "request": request,
            "user": user,
            "model_types": ["classification", "regression", "clustering", "neural_network", "other"]
        }
    )


@router.post("/create")
async def create_model(
        request: Request,
        name: str = Form(...),
        description: str = Form(...),
        model_type: str = Form(...),
        model_file: UploadFile = File(...),
        user=Depends(get_current_user)
):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    file_ext = os.path.splitext(model_file.filename)[1].lower()
    if file_ext[1:] not in Config.ALLOWED_EXTENSIONS:
        return templates.TemplateResponse(
            "models/create.html",
            {
                "request": request,
                "user": user,
                "model_types": ["classification", "regression", "clustering", "neural_network", "other"],
                "error": f"File type not allowed. Allowed types: {', '.join(Config.ALLOWED_EXTENSIONS)}"
            }
        )

    filename = f"{uuid.uuid4()}{file_ext}"
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

    with open(filepath, "wb") as f:
        content = await model_file.read()
        f.write(content)

    try:
        file_id = FileRepository.add(model_file.filename, filename)

        model_id = ResearcherService.create_model(name, description, model_type, file_id)

        return RedirectResponse(url=f"/models/{model_id}", status_code=302)
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)

        return templates.TemplateResponse(
            "models/create.html",
            {
                "request": request,
                "user": user,
                "model_types": ["classification", "regression", "clustering", "neural_network", "other"],
                "error": str(e)
            }
        )


@router.get("/{model_id}", response_class=HTMLResponse)
async def model_detail(request: Request, model_id: int, user=Depends(get_current_user)):
    model = ResearcherService.get_model(model_id)
    if not model:
        return RedirectResponse(url="/models")

    return templates.TemplateResponse(
        "models/detail.html",
        {
            "request": request,
            "user": user,
            "model": model,
            "file_url": f"/static/uploads/{model['file_path']}" if model.get('file_path') else None
        }
    )


@router.get("/{model_id}/edit", response_class=HTMLResponse)
async def edit_model_page(request: Request, model_id: int, user=Depends(get_current_user)):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    model = ModelRepository.get(model_id)
    if not model:
        return RedirectResponse(url="/models")

    return templates.TemplateResponse(
        "models/edit.html",
        {
            "request": request,
            "user": user,
            "model": model,
            "model_types": ["classification", "regression", "clustering", "neural_network", "other"]
        }
    )


@router.post("/{model_id}/update")
async def update_model(
        request: Request,
        model_id: int,
        name: str = Form(None),
        description: str = Form(None),
        model_type: str = Form(None),
        user=Depends(get_current_user)
):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    ModelRepository.update(model_id, name, description, model_type)
    return RedirectResponse(url=f"/models/{model_id}", status_code=302)


@router.post("/{model_id}/delete")
async def delete_model(
        request: Request,
        model_id: int,
        user=Depends(get_current_user)
):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    ModelRepository.delete(model_id)
    return RedirectResponse(url="/models", status_code=302)