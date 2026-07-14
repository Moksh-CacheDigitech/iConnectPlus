"""Integration smoke: Project module imports and router mount."""

from modules.project.models import PrjProject, PrjProjectCost, PrjProjectTask
from modules.project.router import project_router
from modules.project.service import CostService, ProjectApplicationService, ProjectService
from modules.project.service.engines import ProjectCostEngine, ProjectEngine


def test_project_models_importable():
    assert PrjProject.__tablename__ == "prj_project"
    assert PrjProjectTask.__tablename__ == "prj_project_task"
    assert PrjProjectCost.__tablename__ == "prj_project_cost"


def test_project_router_mounted():
    assert project_router.prefix == "/projects"
    assert len(project_router.routes) > 20


def test_project_services_and_engines_importable():
    assert ProjectApplicationService is not None
    assert ProjectService is not None
    assert CostService is not None
    assert ProjectEngine is not None
    assert ProjectCostEngine is not None
