/** Shared API contract types aligned with backend Pydantic schemas. */

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T | null;
}

export interface ErrorResponse {
  success: false;
  message: string;
  errors: string[];
}

export interface HealthData {
  status: string;
  environment: string;
  version: string;
  database: string;
}
