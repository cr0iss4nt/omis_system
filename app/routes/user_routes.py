from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from app.auth import get_current_user
from app.repositories.user_repository import UserRepository
from app.repositories.credentials_repository import CredentialsRepository
from app.services.admin_service import AdminService
#from app.templates import templates
from app.templates_loader import templates

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_class=HTMLResponse)
async def list_users(
        request: Request,
        user=Depends(get_current_user),
        page: int = Query(1, ge=1),
        per_page: int = Query(20, ge=1, le=100)
):
    if user["role"] != "admin":
        return RedirectResponse(url="/dashboard")

    all_users = UserRepository.get_all()
    for user_data in all_users:
        user_data['username'] = CredentialsRepository.get_by_user_id(user_data['id'])

    # Пагинация
    total = len(all_users)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_users = all_users[start:end]

    return templates.TemplateResponse(
        "users/list.html",
        {
            "request": request,
            "user": user,
            "users": paginated_users,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page
        }
    )


@router.get("/create", response_class=HTMLResponse)
async def create_user_page(request: Request, user=Depends(get_current_user)):
    if user["role"] != "admin":
        return RedirectResponse(url="/dashboard")

    return templates.TemplateResponse(
        "users/create.html",
        {"request": request, "user": user}
    )


@router.post("/create")
async def create_user(
        request: Request,
        full_name: str = Form(...),
        email: str = Form(...),
        username: str = Form(...),
        password: str = Form(...),
        role: str = Form(...),
        user=Depends(get_current_user)
):
    if user["role"] != "admin":
        return RedirectResponse(url="/dashboard")

    try:
        user_id = AdminService.create_user(full_name, email, username, password, role)
        return RedirectResponse(url=f"/users/{user_id}", status_code=302)
    except ValueError as e:
        return templates.TemplateResponse(
            "users/create.html",
            {"request": request, "user": user, "error": str(e)}
        )


@router.get("/{user_id}", response_class=HTMLResponse)
async def user_detail(request: Request, user_id: int, user=Depends(get_current_user)):
    if user["role"] != "admin":
        return RedirectResponse(url="/dashboard")

    user_data = UserRepository.get(user_id)
    if not user_data:
        return RedirectResponse(url="/users")

    user_data['username'] = CredentialsRepository.get_by_user_id(user_id)

    return templates.TemplateResponse(
        "users/detail.html",
        {
            "request": request,
            "user": user,
            "user_data": user_data
        }
    )


@router.post("/{user_id}/update")
async def update_user(
        request: Request,
        user_id: int,
        full_name: str = Form(None),
        email: str = Form(None),
        role: str = Form(None),
        password: str = Form(None),
        user=Depends(get_current_user)
):
    if user["role"] != "admin":
        return RedirectResponse(url="/dashboard")

    try:
        AdminService.update_user(user_id, full_name, email, role, password)
        return RedirectResponse(url=f"/users/{user_id}", status_code=302)
    except Exception as e:
        user_data = UserRepository.get(user_id)
        user_data['username'] = CredentialsRepository.get_by_user_id(user_id)

        return templates.TemplateResponse(
            "users/detail.html",
            {
                "request": request,
                "user": user,
                "user_data": user_data,
                "error": str(e)
            }
        )


@router.post("/{user_id}/delete")
async def delete_user(
        request: Request,
        user_id: int,
        user=Depends(get_current_user)
):
    if user["role"] != "admin":
        return RedirectResponse(url="/dashboard")

    AdminService.delete_user(user_id)
    return RedirectResponse(url="/users", status_code=302)