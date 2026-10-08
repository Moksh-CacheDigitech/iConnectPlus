/**
 * Procurement Excel tracker upload — merge new rows/columns into the extracted table.
 */
import { ApiClientError, apiClient } from "@/services/api-client";

const API = "/procurement/scm/sheet-trackers";

export type SheetTrackerMergeInfo = {
  added_columns: string[];
  added_rows: number;
  updated_rows: number;
  file_name: string | null;
};

export type SheetTrackerSummary = {
  id: string;
  name: string;
  last_file_name: string | null;
  column_count: number;
  row_count: number;
  last_upload_at: string | null;
  created_at: string;
  updated_at: string;
  version: number;
  last_merge: SheetTrackerMergeInfo | null;
};

export type SheetTrackerColumn = {
  id: string;
  label: string;
};

export type SheetTrackerDetail = SheetTrackerSummary & {
  columns: SheetTrackerColumn[];
  rows: Record<string, string>[];
};

function unwrap<T>(res: { data: T | null }): T {
  if (res.data == null) {
    throw new ApiClientError("Empty response from server", 500);
  }
  return res.data;
}

export async function listSheetTrackers(): Promise<SheetTrackerSummary[]> {
  const res = await apiClient<SheetTrackerSummary[]>(API);
  return Array.isArray(res.data) ? res.data : [];
}

export async function getSheetTracker(id: string): Promise<SheetTrackerDetail> {
  return unwrap(await apiClient<SheetTrackerDetail>(`${API}/${id}`));
}

export async function uploadSheetTracker(body: {
  file_name: string;
  content_base64: string;
  content_type?: string;
  tracker_id?: string | null;
  name?: string;
}): Promise<SheetTrackerDetail> {
  return unwrap(
    await apiClient<SheetTrackerDetail>(API, {
      method: "POST",
      body,
    }),
  );
}
