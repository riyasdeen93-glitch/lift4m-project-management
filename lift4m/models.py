from __future__ import annotations

import enum
import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional


class Role(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    CUSTOMER = "customer"
    MANUFACTURER = "manufacturer"
    MAINTENANCE_PROVIDER = "maintenance_provider"


class ProjectType(str, enum.Enum):
    NEW_INSTALLATION = "new_installation"
    RETROFIT = "retrofit"
    SERVICE = "service"


@dataclass
class StageDefinition:
    id: int
    name: str
    description: str


@dataclass
class StageInstance:
    definition: StageDefinition
    status: str = "not_started"  # not_started, in_progress, completed, on_hold
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    notes: List[str] = field(default_factory=list)

    def update_status(self, new_status: str, note: Optional[str] = None) -> None:
        if self.status == "not_started" and new_status in {"in_progress", "completed"}:
            self.start_date = datetime.date.today()
        if new_status == "completed":
            self.end_date = datetime.date.today()
        self.status = new_status
        if note:
            ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.notes.append(f"[{ts}] {note}")


@dataclass
class Project:
    id: int
    name: str
    project_type: ProjectType
    customer_id: int
    manufacturer_id: Optional[int] = None
    maintenance_provider_id: Optional[int] = None
    stages: List[StageInstance] = field(default_factory=list)
    meta: Dict[str, str] = field(default_factory=dict)

    def current_stage(self) -> Optional[StageInstance]:
        for stage in self.stages:
            if stage.status != "completed":
                return stage
        return None

    def progress_percentage(self) -> float:
        if not self.stages:
            return 0.0
        completed = sum(1 for s in self.stages if s.status == "completed")
        return completed / len(self.stages) * 100


STAGE_DEFINITIONS: Dict[int, StageDefinition] = {
    1: StageDefinition(1, "Onboarding & Need Discovery",
                       "Capture customer info and high level requirements."),
    2: StageDefinition(2, "Requirement Form & Measurements",
                       "Collect measurements/drawings and schedule surveys."),
    3: StageDefinition(3, "Verified Survey & Feasibility Report",
                       "Onsite assessment and risk grading."),
    4: StageDefinition(4, "Lead Broadcast",
                       "Send the verified lead to manufacturers / service providers."),
    5: StageDefinition(5, "Quote Ranking & Presentation",
                       "AI ranks proposals and presents top options."),
    6: StageDefinition(6, "Selection & Contract",
                       "Customer selects provider and tri-party contract is generated."),
    7: StageDefinition(7, "Technical Freeze (GAD Approval)",
                       "Drawings uploaded and approved by stakeholders."),
    8: StageDefinition(8, "Production & Readiness",
                       "Manufacturing progress and site readiness (JRC)."),
    9: StageDefinition(9, "Delivery & Installation",
                       "Shipment, installation and commissioning."),
    10: StageDefinition(10, "Handover & Support",
                        "Final handover, logbook, warranty and AMC."),
}

STAGE_MAPPINGS: Dict[ProjectType, List[int]] = {
    ProjectType.NEW_INSTALLATION: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    ProjectType.RETROFIT: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    ProjectType.SERVICE: [1, 2, 3, 4, 5, 6, 8, 9, 10],  # condensed for service/AMC
}


def initialise_project(
    project_id: int,
    name: str,
    project_type: ProjectType,
    customer_id: int,
    meta: Optional[Dict[str, str]] = None,
) -> Project:
    stage_ids = STAGE_MAPPINGS[project_type]
    stages = [StageInstance(definition=STAGE_DEFINITIONS[sid]) for sid in stage_ids]
    return Project(
        id=project_id,
        name=name,
        project_type=project_type,
        customer_id=customer_id,
        stages=stages,
        meta=meta or {},
    )
