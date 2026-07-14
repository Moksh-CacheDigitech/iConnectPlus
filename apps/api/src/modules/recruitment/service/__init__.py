"""Recruitment services."""

from modules.recruitment.service.application_service import ApplicationService
from modules.recruitment.service.application_service_facade import RecruitmentApplicationService
from modules.recruitment.service.application_stage_service import ApplicationStageService
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

__all__ = [
    "ApplicationService",
    "ApplicationStageService",
    "BackgroundVerificationService",
    "CandidateDocumentService",
    "CandidateNoteService",
    "CandidateService",
    "InterviewFeedbackService",
    "InterviewService",
    "JobPostingService",
    "JobRequisitionService",
    "OfferApprovalService",
    "OfferService",
    "OnboardingService",
    "OnboardingTaskService",
    "RecruiterService",
    "RecruitmentApplicationService",
    "RecruitmentIntegrationService",
    "RecruitmentReportService",
    "RecruitmentSourceService",
    "ReferenceCheckService",
    "ResumeService",
    "TalentPoolService",
]
