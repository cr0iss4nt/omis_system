from fastapi import APIRouter, Request, Depends, UploadFile, File, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import uuid
from app.auth import get_current_user
from app.repositories.file_repository import FileRepository
from app.config import Config
#from app.templates import templates
from app.templates_loader import templates

router = APIRouter(prefix="/files", tags=["files"])


@router.get("/", response_class=HTMLResponse)
async def list_files(
        request: Request,
        user=Depends(get_current_user),
        page: int = Query(1, ge=1)
):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    files = FileRepository.get_all()

    return templates.TemplateResponse(
        "files/list.html",
        {
            "request": request,
            "user": user,
            "files": files,
            "page": page
        }
    )


@router.get("/upload", response_class=HTMLResponse)
async def upload_file_page(request: Request, user=Depends(get_current_user)):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    return templates.TemplateResponse(
        "files/upload.html",
        {"request": request, "user": user}
    )


@router.post("/upload")
async def upload_file(
        request: Request,
        file: UploadFile = File(...),
        description: str = Form(""),
        user=Depends(get_current_user)
):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    # Проверяем расширение файла
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext[1:] not in Config.ALLOWED_EXTENSIONS:
        return templates.TemplateResponse(
            "files/upload.html",
            {
                "request": request,
                "user": user,
                "error": f"File type not allowed. Allowed types: {', '.join(Config.ALLOWED_EXTENSIONS)}"
            }
        )

    # Сохраняем файл
    filename = f"{uuid.uuid4()}{file_ext}"
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    # Сохраняем запись в БД
    file_id = FileRepository.add(file.filename, filename)

    return RedirectResponse(url=f"/files/{file_id}", status_code=302)


@router.get("/{file_id}", response_class=HTMLResponse)
async def file_detail(request: Request, file_id: int, user=Depends(get_current_user)):
    file_data = FileRepository.get(file_id)
    if not file_data:
        return RedirectResponse(url="/files")

    return templates.TemplateResponse(
        "files/detail.html",
        {
            "request": request,
            "user": user,
            "file": file_data,
            "file_url": f"/static/uploads/{file_data['path']}"
        }
    )


@router.post("/{file_id}/delete")
async def delete_file(
        request: Request,
        file_id: int,
        user=Depends(get_current_user)
):
    if user["role"] not in ["researcher", "admin"]:
        return RedirectResponse(url="/dashboard")

    file_data = FileRepository.get(file_id)
    if file_data:
        # Удаляем физический файл
        filepath = os.path.join(Config.UPLOAD_FOLDER, file_data['path'])
        if os.path.exists(filepath):
            os.remove(filepath)

        # Удаляем запись из БД
        FileRepository.delete(file_id)

    return RedirectResponse(url="/files", status_code=302)