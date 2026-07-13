import { env } from "@/utils/env";
import type { ApiResponse, ErrorResponse } from "@/types/api";

export class ApiClientError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly errors: string[] = [],
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
};

/**
 * Foundation HTTP client for all API communication.
 * UI must never access the database directly (DG-01).
 */
export async function apiClient<T>(
  path: string,
  options: RequestOptions = {},
): Promise<ApiResponse<T>> {
  const { body, headers, ...rest } = options;

  const response = await fetch(`${env.apiUrl}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
    cache: "no-store",
  });

  const payload = (await response.json()) as ApiResponse<T> | ErrorResponse;

  if (!response.ok || payload.success === false) {
    const errorPayload = payload as ErrorResponse;
    throw new ApiClientError(
      errorPayload.message ?? "API request failed",
      response.status,
      errorPayload.errors ?? [],
    );
  }

  return payload as ApiResponse<T>;
}

export const healthService = {
  check: () => apiClient<Record<string, string>>("/health"),
};
