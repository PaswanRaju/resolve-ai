// Typed helpers for calling the FastAPI backend. Only imported by server code
// (server components and server actions), so BACKEND_URL never reaches the browser.
import "server-only";

export type Priority = "1-critical" | "2-high" | "3-moderate" | "4-low";
export type Status = "new" | "in_progress" | "on_hold" | "resolved" | "closed";

export type WorkNote = { author: string; body: string; created_at: string };

export type Ticket = {
  number: string;
  short_description: string;
  description: string;
  category: string;
  priority: Priority;
  caller: string;
  status: Status;
  assignment_group: string | null;
  work_notes: WorkNote[];
  resolution_notes: string | null;
  resolved_by: string | null;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
};

export type TicketList = { items: Ticket[]; total: number; limit: number; skip: number };

export const PRIORITIES: Priority[] = ["1-critical", "2-high", "3-moderate", "4-low"];
export const STATUSES: Status[] = ["new", "in_progress", "on_hold", "resolved", "closed"];

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

const BASE = process.env.BACKEND_URL ?? "http://localhost:8000";

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail = typeof body.detail === "string" ? body.detail : res.statusText;
    throw new ApiError(res.status, detail);
  }
  return (await res.json()) as T;
}

export function label(value: string): string {
  return value.replace(/^\d-/, "").replace("_", " ");
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" });
}
