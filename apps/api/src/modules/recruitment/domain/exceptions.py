"""Recruitment domain exceptions."""

from core.exceptions import ConflictException


class InvalidJobRequisitionState(ConflictException):
    def __init__(self, message: str = "Invalid jobrequisition state") -> None:
        super().__init__(message)

class InvalidJobPostingState(ConflictException):
    def __init__(self, message: str = "Invalid jobposting state") -> None:
        super().__init__(message)

class InvalidRecruitmentSourceState(ConflictException):
    def __init__(self, message: str = "Invalid recruitmentsource state") -> None:
        super().__init__(message)

class InvalidRecruiterState(ConflictException):
    def __init__(self, message: str = "Invalid recruiter state") -> None:
        super().__init__(message)

class InvalidCandidateState(ConflictException):
    def __init__(self, message: str = "Invalid candidate state") -> None:
        super().__init__(message)

class InvalidCandidateDocumentState(ConflictException):
    def __init__(self, message: str = "Invalid candidatedocument state") -> None:
        super().__init__(message)

class InvalidResumeState(ConflictException):
    def __init__(self, message: str = "Invalid resume state") -> None:
        super().__init__(message)

class InvalidApplicationState(ConflictException):
    def __init__(self, message: str = "Invalid application state") -> None:
        super().__init__(message)

class InvalidApplicationStageState(ConflictException):
    def __init__(self, message: str = "Invalid applicationstage state") -> None:
        super().__init__(message)

class InvalidInterviewState(ConflictException):
    def __init__(self, message: str = "Invalid interview state") -> None:
        super().__init__(message)

class InvalidInterviewFeedbackState(ConflictException):
    def __init__(self, message: str = "Invalid interviewfeedback state") -> None:
        super().__init__(message)

class InvalidOfferState(ConflictException):
    def __init__(self, message: str = "Invalid offer state") -> None:
        super().__init__(message)

class InvalidOfferApprovalState(ConflictException):
    def __init__(self, message: str = "Invalid offerapproval state") -> None:
        super().__init__(message)

class InvalidBackgroundVerificationState(ConflictException):
    def __init__(self, message: str = "Invalid backgroundverification state") -> None:
        super().__init__(message)

class InvalidReferenceCheckState(ConflictException):
    def __init__(self, message: str = "Invalid referencecheck state") -> None:
        super().__init__(message)

class InvalidTalentPoolState(ConflictException):
    def __init__(self, message: str = "Invalid talentpool state") -> None:
        super().__init__(message)

class InvalidCandidateNoteState(ConflictException):
    def __init__(self, message: str = "Invalid candidatenote state") -> None:
        super().__init__(message)

class InvalidOnboardingState(ConflictException):
    def __init__(self, message: str = "Invalid onboarding state") -> None:
        super().__init__(message)

class InvalidOnboardingTaskState(ConflictException):
    def __init__(self, message: str = "Invalid onboardingtask state") -> None:
        super().__init__(message)

class InvalidRecruitmentReportState(ConflictException):
    def __init__(self, message: str = "Invalid recruitmentreport state") -> None:
        super().__init__(message)
