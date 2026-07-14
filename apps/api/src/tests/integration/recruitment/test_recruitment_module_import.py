"""Integration smoke: Recruitment module imports and router mount."""

from modules.recruitment.models import RecApplication, RecCandidate, RecJobRequisition
from modules.recruitment.router import recruitment_router
from modules.recruitment.service import (
    JobRequisitionService,
    OfferService,
    RecruitmentApplicationService,
)
from modules.recruitment.service.engines import JobRequisitionEngine, OfferEngine


def test_recruitment_models_importable():
    assert RecJobRequisition.__tablename__ == "rec_job_requisition"
    assert RecCandidate.__tablename__ == "rec_candidate"
    assert RecApplication.__tablename__ == "rec_application"


def test_recruitment_router_mounted():
    assert recruitment_router.prefix == "/recruitment"
    assert len(recruitment_router.routes) > 20


def test_recruitment_services_and_engines_importable():
    assert RecruitmentApplicationService is not None
    assert JobRequisitionService is not None
    assert OfferService is not None
    assert JobRequisitionEngine is not None
    assert OfferEngine is not None
