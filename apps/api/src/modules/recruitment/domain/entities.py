"""Recruitment domain entity markers."""

from enum import Enum


class RecAggregate(str, Enum):
    JOBREQUISITION = "rec_job_requisition"
    JOBPOSTING = "rec_job_posting"
    RECRUITMENTSOURCE = "rec_recruitment_source"
    RECRUITER = "rec_recruiter"
    CANDIDATE = "rec_candidate"
    CANDIDATEDOCUMENT = "rec_candidate_document"
    RESUME = "rec_resume"
    APPLICATION = "rec_application"
    APPLICATIONSTAGE = "rec_application_stage"
    INTERVIEW = "rec_interview"
    INTERVIEWFEEDBACK = "rec_interview_feedback"
    OFFER = "rec_offer"
    OFFERAPPROVAL = "rec_offer_approval"
    BACKGROUNDVERIFICATION = "rec_background_verification"
    REFERENCECHECK = "rec_reference_check"
    TALENTPOOL = "rec_talent_pool"
    CANDIDATENOTE = "rec_candidate_note"
    ONBOARDING = "rec_onboarding"
    ONBOARDINGTASK = "rec_onboarding_task"
    RECRUITMENTREPORT = "rec_recruitment_report"
