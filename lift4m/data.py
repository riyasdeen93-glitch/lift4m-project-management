from __future__ import annotations

from typing import Dict, List

from .models import Role, ProjectType, initialise_project, Project


class User:
    def __init__(self, user_id: int, name: str, role: Role):
        self.id = user_id
        self.name = name
        self.role = role


USERS: Dict[int, User] = {
    1: User(1, "Super Admin", Role.SUPER_ADMIN),
    2: User(2, "Alice Builder", Role.CUSTOMER),
    3: User(3, "LiftCo Manufacturing", Role.MANUFACTURER),
    4: User(4, "ServicePro Maint", Role.MAINTENANCE_PROVIDER),
}


def _create_sample_projects() -> List[Project]:
    p1 = initialise_project(
        project_id=101,
        name="Sunshine Apartments Lift",
        project_type=ProjectType.NEW_INSTALLATION,
        customer_id=2,
        meta={
            "address": "Sunshine Apartments, Main Street, Chennai",
            "capacity": "6 persons",
            "building_type": "Residential",
        },
    )
    p1.stages[0].update_status(
        "completed", "Account created and requirements captured"
    )
    p1.stages[1].update_status(
        "completed", "Measurements and drawings provided"
    )
    p1.stages[2].update_status(
        "in_progress", "Survey scheduled for tomorrow"
    )

    p2 = initialise_project(
        project_id=102,
        name="Mall Escalator Service",
        project_type=ProjectType.SERVICE,
        customer_id=2,
        meta={"address": "City Mall, Chennai", "equipment": "Escalator #3"},
    )
    p2.stages[0].update_status(
        "completed", "Service request logged via app"
    )
    p2.stages[1].update_status(
        "in_progress", "Issue description and photos uploaded"
    )

    return [p1, p2]


PROJECTS: Dict[int, Project] = {p.id: p for p in _create_sample_projects()}


def get_projects_for_user(user: User) -> List[Project]:
    if user.role == Role.SUPER_ADMIN:
        return list(PROJECTS.values())
    if user.role == Role.CUSTOMER:
        return [p for p in PROJECTS.values() if p.customer_id == user.id]
    if user.role == Role.MANUFACTURER:
        return [p for p in PROJECTS.values() if p.manufacturer_id == user.id]
    if user.role == Role.MAINTENANCE_PROVIDER:
        return [p for p in PROJECTS.values() if p.maintenance_provider_id == user.id]
    return []


def assign_manufacturer(project_id: int, manufacturer_id: int) -> None:
    project = PROJECTS.get(project_id)
    if project:
        project.manufacturer_id = manufacturer_id


def assign_maintenance_provider(project_id: int, provider_id: int) -> None:
    project = PROJECTS.get(project_id)
    if project:
        project.maintenance_provider_id = provider_id
