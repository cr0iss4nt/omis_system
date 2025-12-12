from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime, date
from app.auth import get_current_user
from app.repositories.experiment_repository import ExperimentRepository
from app.services.teacher_service import TeacherService
from app.services.student_service import StudentService
from app.templates_loader import templates

router = APIRouter(prefix="/labs", tags=["labs"])


@router.get("/", response_class=HTMLResponse)
async def list_labs(
        request: Request,
        user=Depends(get_current_user),
        page: int = Query(1, ge=1)
):
    if user["role"] not in ["teacher", "admin"]:
        return RedirectResponse(url="/dashboard")

    labs = TeacherService.get_labs()

    return templates.TemplateResponse(
        "labs/list.html",
        {
            "request": request,
            "user": user,
            "labs": labs,
            "page": page
        }
    )


@router.get("/create", response_class=HTMLResponse)
async def create_lab_page(request: Request, user=Depends(get_current_user)):
    if user["role"] not in ["teacher", "admin"]:
        return RedirectResponse(url="/dashboard")

    experiments = ExperimentRepository.get_all()

    return templates.TemplateResponse(
        "labs/create.html",
        {
            "request": request,
            "user": user,
            "experiments": experiments
        }
    )


@router.post("/create")
async def create_lab(
        request: Request,
        name: str = Form(...),
        instruction: str = Form(...),
        deadline: str = Form(...),
        experiment_id: int = Form(...),
        user=Depends(get_current_user)
):
    if user["role"] not in ["teacher", "admin"]:
        return RedirectResponse(url="/dashboard")

    try:
        deadline_dt = datetime.fromisoformat(deadline)
        lab_id = TeacherService.create_lab(name, instruction, deadline_dt, experiment_id)

        return RedirectResponse(url=f"/labs/{lab_id}", status_code=302)
    except ValueError as e:
        experiments = ExperimentRepository.get_all()
        return templates.TemplateResponse(
            "labs/create.html",
            {
                "request": request,
                "user": user,
                "experiments": experiments,
                "error": "Invalid date format. Please use YYYY-MM-DD HH:MM:SS"
            }
        )


@router.get("/{lab_id}", response_class=HTMLResponse)
async def lab_detail(request: Request, lab_id: int, user=Depends(get_current_user)):
    if user["role"] not in ["teacher", "admin"]:
        return RedirectResponse(url="/dashboard")

    lab = TeacherService.get_lab(lab_id)
    if not lab:
        return RedirectResponse(url="/labs")

    return templates.TemplateResponse(
        "labs/detail.html",
        {
            "request": request,
            "user": user,
            "lab": lab
        }
    )


@router.get("/{lab_id}/assign", response_class=HTMLResponse)
async def assign_lab_page(request: Request, lab_id: int, user=Depends(get_current_user)):
    if user["role"] not in ["teacher", "admin"]:
        return RedirectResponse(url="/dashboard")

    students = TeacherService.get_students()

    return templates.TemplateResponse(
        "labs/assign.html",
        {
            "request": request,
            "user": user,
            "lab_id": lab_id,
            "students": students
        }
    )


@router.post("/{lab_id}/assign")
async def assign_lab(
        request: Request,
        lab_id: int,
        student_ids: list = Form(...),
        user=Depends(get_current_user)
):
    if user["role"] not in ["teacher", "admin"]:
        return RedirectResponse(url="/dashboard")

    for student_id in student_ids:
        TeacherService.assign_lab(lab_id, int(student_id))

    return RedirectResponse(url=f"/labs/{lab_id}", status_code=302)


@router.post("/{lab_id}/grade")
async def grade_lab(
        request: Request,
        lab_id: int,
        student_id: int = Form(...),
        grade: float = Form(...),
        user=Depends(get_current_user)
):
    if user["role"] not in ["teacher", "admin"]:
        return RedirectResponse(url="/dashboard")

    TeacherService.grade_lab(lab_id, student_id, grade)
    return RedirectResponse(url=f"/labs/{lab_id}", status_code=302)


@router.get("/student/mylabs", response_class=HTMLResponse)
async def student_labs(request: Request, user=Depends(get_current_user)):
    if user["role"] != "student":
        return RedirectResponse(url="/dashboard")

    student_id = int(user['sub'])
    labs = StudentService.get_my_labs(student_id)

    return templates.TemplateResponse(
        "labs/student_list.html",
        {
            "request": request,
            "user": user,
            "labs": labs,
            "now": date.today()
        }
    )


@router.get("/student/{lab_id}", response_class=HTMLResponse)
async def student_lab_detail(request: Request, lab_id: int, user=Depends(get_current_user)):
    if user["role"] != "student":
        return RedirectResponse(url="/dashboard")

    student_id = int(user['sub'])
    lab = StudentService.get_lab_details(lab_id, student_id)

    if not lab:
        return RedirectResponse(url="/labs/student/mylabs")

    return templates.TemplateResponse(
        "labs/student_detail.html",
        {
            "request": request,
            "user": user,
            "lab": lab,
            "now": date.today()
        }
    )


@router.post("/student/{lab_id}/submit")
async def submit_lab(
        request: Request,
        lab_id: int,
        submission: str = Form(...),
        user=Depends(get_current_user)
):
    if user["role"] != "student":
        return RedirectResponse(url="/dashboard")

    student_id = int(user['sub'])
    StudentService.submit_lab(lab_id, student_id, submission)

    return RedirectResponse(url=f"/labs/student/{lab_id}", status_code=302)