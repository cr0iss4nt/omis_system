from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import traceback
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from app.config import Config

app = FastAPI(title="ML Experiment Management System", debug=True)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates and static files
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Create necessary directories
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
os.makedirs("app/templates/auth", exist_ok=True)
os.makedirs("app/static/css", exist_ok=True)
os.makedirs("app/static/js", exist_ok=True)


# Добавляем фильтры для Jinja2
def nl2br(value):
    """Convert newlines to <br> tags."""
    if not value:
        return ''
    return value.replace('\n', '<br>\n')


def truncate(value, length=50, suffix='...'):
    """Truncate a string."""
    if len(value) <= length:
        return value
    return value[:length] + suffix


templates.env.filters['nl2br'] = nl2br
templates.env.filters['truncate'] = truncate

# Теперь импортируем роутеры
from app.routes import auth_routes, user_routes, file_routes, model_routes, experiment_routes, lab_routes

# Include routers
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(file_routes.router)
app.include_router(model_routes.router)
app.include_router(experiment_routes.router)
app.include_router(lab_routes.router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        from app.auth import get_current_user
        user = get_current_user(request)
        logger.info(f"Home: User authenticated: {user}")
        return RedirectResponse(url="/dashboard")
    except Exception as e:
        logger.info(f"Home: Not authenticated, redirecting to login: {e}")
        return templates.TemplateResponse("auth/login.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    try:
        from app.auth import get_current_user
        user = get_current_user(request)
        logger.info(f"Dashboard: User: {user}")
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "user": user, "now": datetime.utcnow()}
        )
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return RedirectResponse(url="/login")


# Глобальный обработчик ошибок
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error handler: {exc}")
    logger.error(traceback.format_exc())

    # Если это HTML запрос, показываем страницу с ошибкой
    if "text/html" in request.headers.get("accept", ""):
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(exc)},
            status_code=500
        )
    # Иначе возвращаем JSON
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)}
    )