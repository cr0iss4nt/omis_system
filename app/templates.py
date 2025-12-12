from fastapi.templating import Jinja2Templates
import os

# Создаем объект templates для использования во всех модулях
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)