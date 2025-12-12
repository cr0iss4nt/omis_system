from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from app.database import get_db_cursor
from app.auth import create_access_token, get_current_user
from app.repositories.user_repository import UserRepository
from app.repositories.credentials_repository import CredentialsRepository
from app.services.controller_factory import ControllerFactory
from app.main import templates
from app.templates_loader import templates

router = APIRouter(prefix="", tags=["auth"])


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)
):
    try:
        user_id = CredentialsRepository.auth(username, password)

        if not user_id:
            return templates.TemplateResponse(
                "auth/login.html",
                {"request": request, "error": "Invalid username or password"}
            )

        user = UserRepository.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        token = create_access_token(user_id, user["role"])

        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="access_token", value=token, httponly=True)
        return response
    except Exception as e:
        print(f"Login error: {e}")
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": f"Login failed: {str(e)}"}
        )


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/register")
async def register(
        request: Request,
        full_name: str = Form(...),
        email: str = Form(...),
        username: str = Form(...),
        password: str = Form(...),
        role: str = Form(...)
):
    try:
        with get_db_cursor() as cur:
            # Check if email exists
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                return templates.TemplateResponse(
                    "auth/register.html",
                    {"request": request, "error": "Email already registered"}
                )

            # Check if username exists
            cur.execute("SELECT id FROM credentials WHERE username = %s", (username,))
            if cur.fetchone():
                return templates.TemplateResponse(
                    "auth/register.html",
                    {"request": request, "error": "Username already taken"}
                )

            # Create user
            cur.execute(
                "INSERT INTO users(full_name, email, user_role) VALUES (%s, %s, %s) RETURNING id",
                (full_name, email, role)
            )
            user_id = cur.fetchone()[0]

            # Create credentials
            import hashlib
            from passlib.hash import bcrypt
            password_sha256 = hashlib.sha256(password.encode()).hexdigest()
            hashed = bcrypt.hash(password_sha256)

            cur.execute(
                "INSERT INTO credentials(id, username, pass) VALUES (%s, %s, %s)",
                (user_id, username, hashed)
            )

        # Auto login
        token = create_access_token(user_id, role)
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="access_token", value=token, httponly=True)
        return response
    except Exception as e:
        print(f"Registration error: {e}")
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": f"Registration failed: {str(e)}"}
        )


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, user=Depends(get_current_user)):
    try:
        user_details = UserRepository.get(int(user['sub']))
        username = CredentialsRepository.get_by_user_id(int(user['sub']))

        return templates.TemplateResponse(
            "users/profile.html",
            {
                "request": request,
                "user": user,
                "user_details": user_details,
                "username": username
            }
        )
    except Exception as e:
        print(f"Profile error: {e}")
        response = RedirectResponse(url="/login", status_code=302)
        response.delete_cookie(key="access_token")
        return response


@router.post("/profile/update")
async def update_profile(
        request: Request,
        full_name: str = Form(None),
        email: str = Form(None),
        current_password: str = Form(None),
        new_password: str = Form(None),
        user=Depends(get_current_user)
):
    try:
        user_id = int(user['sub'])

        updates = {}
        if full_name:
            updates['full_name'] = full_name
        if email:
            updates['email'] = email

        if updates:
            UserRepository.update(user_id, **updates)

        if current_password and new_password:
            # Verify current password
            username = CredentialsRepository.get_by_user_id(user_id)
            if CredentialsRepository.auth(username, current_password):
                CredentialsRepository.update_password(user_id, new_password)
            else:
                return templates.TemplateResponse(
                    "users/profile.html",
                    {
                        "request": request,
                        "user": user,
                        "error": "Current password is incorrect"
                    }
                )

        return RedirectResponse(url="/profile", status_code=302)
    except Exception as e:
        print(f"Update profile error: {e}")
        return templates.TemplateResponse(
            "users/profile.html",
            {
                "request": request,
                "user": user,
                "error": f"Update failed: {str(e)}"
            }
        )