"""Recruitment Pydantic schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class JobRequisitionCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class JobRequisitionUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class JobRequisitionResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class JobPostingCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class JobPostingUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class JobPostingResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class RecruitmentSourceCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class RecruitmentSourceUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class RecruitmentSourceResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class RecruiterCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class RecruiterUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class RecruiterResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class CandidateCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class CandidateUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class CandidateResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class CandidateDocumentCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class CandidateDocumentUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class CandidateDocumentResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ResumeCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ResumeUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ResumeResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ApplicationCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class ApplicationUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ApplicationResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ApplicationStageCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ApplicationStageUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ApplicationStageResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class InterviewCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class InterviewUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class InterviewResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class InterviewFeedbackCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class InterviewFeedbackUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class InterviewFeedbackResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class OfferCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class OfferUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class OfferResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class OfferApprovalCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class OfferApprovalUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class OfferApprovalResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class BackgroundVerificationCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class BackgroundVerificationUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class BackgroundVerificationResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class ReferenceCheckCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class ReferenceCheckUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class ReferenceCheckResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class TalentPoolCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class TalentPoolUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class TalentPoolResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class CandidateNoteCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class CandidateNoteUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class CandidateNoteResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class OnboardingCreate(BaseModel):
    company_id: UUID | None = None
    branch_id: UUID
    status: str | None = None

class OnboardingUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class OnboardingResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class OnboardingTaskCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class OnboardingTaskUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class OnboardingTaskResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class RecruitmentReportCreate(BaseModel):
    company_id: UUID | None = None
    status: str | None = None

class RecruitmentReportUpdate(BaseModel):
    status: str | None = None
    version: int | None = None

class RecruitmentReportResponse(OrmModel):
    id: UUID
    company_id: UUID
    status: str
    version: int

class OnboardingCompleteRequest(BaseModel):
    designation: str
