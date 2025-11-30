from __future__ import annotations

import datetime
from typing import Optional

from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .models import Role
from .data import (
    USERS,
    PROJECTS,
    get_projects_for_user,
    assign_manufacturer,
    assign_maintenance_provider,
)

app = FastAPI(title="Lift4M Demo Platform")

app.mount("/static", StaticFiles(directory="lift4m/static"), name="static")
templates = Jinja2Templates(directory="lift4m/templates")


def get_user(user_id: Optional[int]):
    if user_id is None:
        return None
    return USERS.get(int(user_id))


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "users": USERS, "user": None},
    )


@app.get("/dashboard")
async def dashboard(request: Request, user_id: Optional[int] = None):
    user = get_user(user_id)
    if user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    projects = get_projects_for_user(user)
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "projects": projects,
            "Role": Role,
            "USERS": USERS,
        },
    )


@app.get("/project/{project_id}")
async def view_project(
    request: Request, project_id: int, user_id: Optional[int] = None
):
    user = get_user(user_id)
    project = PROJECTS.get(project_id)
    if user is None or project is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    if user.role != Role.SUPER_ADMIN:
        if user.role == Role.CUSTOMER and project.customer_id != user.id:
            return RedirectResponse(
                url=f"/dashboard?user_id={user.id}",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        if user.role == Role.MANUFACTURER and project.manufacturer_id != user.id:
            return RedirectResponse(
                url=f"/dashboard?user_id={user.id}",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        if (
            user.role == Role.MAINTENANCE_PROVIDER
            and project.maintenance_provider_id != user.id
        ):
            return RedirectResponse(
                url=f"/dashboard?user_id={user.id}",
                status_code=status.HTTP_303_SEE_OTHER,
            )

    return templates.TemplateResponse(
        "project.html",
        {
            "request": request,
            "user": user,
            "project": project,
            "today": datetime.date.today(),
            "Role": Role,
            "USERS": USERS,
        },
    )


@app.get("/project/{project_id}/stage/update")
async def update_stage_status(
    request: Request,
    project_id: int,
    stage_index: int,
    new_status: str,
    note: Optional[str] = None,
    user_id: Optional[int] = None,
):
    user = get_user(user_id)
    project = PROJECTS.get(project_id)
    if user is None or project is None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    allowed = False
    if user.role == Role.SUPER_ADMIN:
        allowed = True
    elif user.role == Role.MANUFACTURER and project.manufacturer_id == user.id:
        allowed = True
    elif (
        user.role == Role.MAINTENANCE_PROVIDER
        and project.maintenance_provider_id == user.id
    ):
        allowed = True

    if not allowed:
        return RedirectResponse(
            url=f"/project/{project_id}?user_id={user.id}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if 0 <= stage_index < len(project.stages):
        project.stages[stage_index].update_status(new_status, note=note)

    return RedirectResponse(
        url=f"/project/{project_id}?user_id={user.id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/project/{project_id}/assign_manufacturer")
async def assign_manufacturer_endpoint(
    request: Request,
    project_id: int,
    manufacturer_id: int,
    user_id: Optional[int] = None,
):
    user = get_user(user_id)
    if user is None or user.role != Role.SUPER_ADMIN:
        return RedirectResponse(
            url=f"/project/{project_id}?user_id={user.id if user else ''}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    assign_manufacturer(project_id, manufacturer_id)
    return RedirectResponse(
        url=f"/project/{project_id}?user_id={user.id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@app.get("/project/{project_id}/assign_maintenance")
async def assign_maintenance_endpoint(
    request: Request,
    project_id: int,
    provider_id: int,
    user_id: Optional[int] = None,
):
    user = get_user(user_id)
    if user is None or user.role != Role.SUPER_ADMIN:
        return RedirectResponse(
            url=f"/project/{project_id}?user_id={user.id if user else ''}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    assign_maintenance_provider(project_id, provider_id)
    return RedirectResponse(
        url=f"/project/{project_id}?user_id={user.id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "lift4m.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
