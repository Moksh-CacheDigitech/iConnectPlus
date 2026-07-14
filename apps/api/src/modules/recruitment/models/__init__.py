"""Recruitment ORM models."""

from modules.recruitment.models.application import RecApplication
from modules.recruitment.models.application_stage import RecApplicationStage
from modules.recruitment.models.background_verification import RecBackgroundVerification
from modules.recruitment.models.candidate import RecCandidate
from modules.recruitment.models.candidate_document import RecCandidateDocument
from modules.recruitment.models.candidate_note import RecCandidateNote
from modules.recruitment.models.interview import RecInterview
from modules.recruitment.models.interview_feedback import RecInterviewFeedback
from modules.recruitment.models.job_posting import RecJobPosting
from modules.recruitment.models.job_requisition import RecJobRequisition
from modules.recruitment.models.offer import RecOffer
from modules.recruitment.models.offer_approval import RecOfferApproval
from modules.recruitment.models.onboarding import RecOnboarding
from modules.recruitment.models.onboarding_task import RecOnboardingTask
from modules.recruitment.models.recruiter import RecRecruiter
from modules.recruitment.models.recruitment_report import RecRecruitmentReport
from modules.recruitment.models.recruitment_source import RecRecruitmentSource
from modules.recruitment.models.reference_check import RecReferenceCheck
from modules.recruitment.models.resume import RecResume
from modules.recruitment.models.talent_pool import RecTalentPool

__all__ = [
    "RecJobRequisition",
    "RecJobPosting",
    "RecRecruitmentSource",
    "RecRecruiter",
    "RecCandidate",
    "RecCandidateDocument",
    "RecResume",
    "RecApplication",
    "RecApplicationStage",
    "RecInterview",
    "RecInterviewFeedback",
    "RecOffer",
    "RecOfferApproval",
    "RecBackgroundVerification",
    "RecReferenceCheck",
    "RecTalentPool",
    "RecCandidateNote",
    "RecOnboarding",
    "RecOnboardingTask",
    "RecRecruitmentReport",
]
