from fastapi.templating import Jinja2Templates
import os

# Create templates object
templates = Jinja2Templates(directory="app/templates")

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