"use server";

// Server actions: functions the forms call. They run on the Next.js server,
// call the backend, then refresh or redirect the page.
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

import { api, type Ticket } from "@/lib/api";

function text(form: FormData, key: string): string {
  return String(form.get(key) ?? "").trim();
}

export async function createTicket(form: FormData) {
  const ticket = await api<Ticket>("/tickets", {
    method: "POST",
    body: JSON.stringify({
      short_description: text(form, "short_description"),
      description: text(form, "description"),
      category: text(form, "category") || "general",
      priority: text(form, "priority"),
      caller: text(form, "caller"),
    }),
  });
  redirect(`/tickets/${ticket.number}`);
}

export async function updateTicket(number: string, form: FormData) {
  await api<Ticket>(`/tickets/${number}`, {
    method: "PATCH",
    body: JSON.stringify({
      status: text(form, "status"),
      priority: text(form, "priority"),
      assignment_group: text(form, "assignment_group") || null,
    }),
  });
  revalidatePath(`/tickets/${number}`);
}

export async function addWorkNote(number: string, form: FormData) {
  await api<Ticket>(`/tickets/${number}/work-notes`, {
    method: "POST",
    body: JSON.stringify({ author: text(form, "author"), body: text(form, "body") }),
  });
  revalidatePath(`/tickets/${number}`);
}

export async function resolveTicket(number: string, form: FormData) {
  await api<Ticket>(`/tickets/${number}/resolve`, {
    method: "POST",
    body: JSON.stringify({
      resolution_notes: text(form, "resolution_notes"),
      resolved_by: text(form, "resolved_by"),
    }),
  });
  revalidatePath(`/tickets/${number}`);
}
