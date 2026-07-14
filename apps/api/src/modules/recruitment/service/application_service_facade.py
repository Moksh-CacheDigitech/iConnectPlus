"""Recruitment application service facade."""

from sqlalchemy.orm import Session

from modules.recruitment.service.application_service import ApplicationService
from modules.recruitment.service.background_verification_service import (
    BackgroundVerificationService,
)
from modules.recruitment.service.candidate_document_service import CandidateDocumentService
from modules.recruitment.service.candidate_note_service import CandidateNoteService
from modules.recruitment.service.candidate_service import CandidateService
from modules.recruitment.service.integration_service import RecruitmentIntegrationService
from modules.recruitment.service.interview_feedback_service import InterviewFeedbackService
from modules.recruitment.service.interview_service import InterviewService
from modules.recruitment.service.job_posting_service import JobPostingService
from modules.recruitment.service.job_requisition_service import JobRequisitionService
from modules.recruitment.service.offer_approval_service import OfferApprovalService
from modules.recruitment.service.offer_service import OfferService
from modules.recruitment.service.onboarding_service import OnboardingService
from modules.recruitment.service.onboarding_task_service import OnboardingTaskService
from modules.recruitment.service.recruiter_service import RecruiterService
from modules.recruitment.service.recruitment_report_service import RecruitmentReportService
from modules.recruitment.service.recruitment_source_service import RecruitmentSourceService
from modules.recruitment.service.reference_check_service import ReferenceCheckService
from modules.recruitment.service.resume_service import ResumeService
from modules.recruitment.service.talent_pool_service import TalentPoolService


class RecruitmentApplicationService:
    def __init__(self, db: Session) -> None:
        self.requisitions = JobRequisitionService(db)
        self.postings = JobPostingService(db)
        self.sources = RecruitmentSourceService(db)
        self.recruiters = RecruiterService(db)
        self.candidates = CandidateService(db)
        self.documents = CandidateDocumentService(db)
        self.resumes = ResumeService(db)
        self.applications = ApplicationService(db)
        self.interviews = InterviewService(db)
        self.feedback = InterviewFeedbackService(db)
        self.offers = OfferService(db)
        self.offer_approvals = OfferApprovalService(db)
        self.verifications = BackgroundVerificationService(db)
        self.references = ReferenceCheckService(db)
        self.talent_pools = TalentPoolService(db)
        self.notes = CandidateNoteService(db)
        self.onboarding = OnboardingService(db)
        self.onboarding_tasks = OnboardingTaskService(db)
        self.reports = RecruitmentReportService(db)
        self.integration = RecruitmentIntegrationService(db)
