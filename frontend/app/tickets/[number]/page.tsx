import Link from "next/link";
import { notFound } from "next/navigation";

import { api, ApiError, formatDate, label, PRIORITIES, STATUSES, type Ticket } from "@/lib/api";

import { addWorkNote, resolveTicket, updateTicket } from "../actions";

export const dynamic = "force-dynamic";

type Props = { params: Promise<{ number: string }> };

async function loadTicket(number: string): Promise<Ticket> {
  try {
    return await api<Ticket>(`/tickets/${number}`);
  } catch (err) {
    if (err instanceof ApiError && (err.status === 404 || err.status === 422)) notFound();
    throw err;
  }
}

export default async function TicketPage({ params }: Props) {
  const { number } = await params;
  const t = await loadTicket(number);
  const closed = t.status === "closed";
  const resolved = t.status === "resolved";

  // .bind pre-fills the ticket number, so each form only sends its own fields.
  const update = updateTicket.bind(null, t.number);
  const note = addWorkNote.bind(null, t.number);
  const resolve = resolveTicket.bind(null, t.number);

  return (
    <main className="container">
      <p>
        <Link href="/tickets">← All tickets</Link>
      </p>
      <div className="page-head">
        <h1>
          {t.number}: {t.short_description}
        </h1>
      </div>
      <p className="muted">
        Opened by {t.caller} on {formatDate(t.created_at)} · {t.category} ·{" "}
        <span className={`pill p${t.priority[0]}`}>{label(t.priority)}</span>{" "}
        <span className={`pill s-${t.status}`}>{label(t.status)}</span>
      </p>

      <section className="card">
        <h2>Description</h2>
        <p className="pre">{t.description}</p>
      </section>

      {t.resolution_notes && (
        <section className="card resolved">
          <h2>Resolution</h2>
          <p className="pre">{t.resolution_notes}</p>
          <p className="muted">
            Resolved by {t.resolved_by}
            {t.resolved_at && ` on ${formatDate(t.resolved_at)}`}
          </p>
        </section>
      )}

      {!closed && (
        <section className="card">
          <h2>Update</h2>
          {/* key: remount the form after each change so the fields show the saved values. */}
          <form action={update} className="form" key={t.updated_at}>
            <div className="row">
              <label>
                Status
                <select name="status" defaultValue={t.status}>
                  {STATUSES.filter((s) => s !== "resolved" || resolved).map((s) => (
                    <option key={s} value={s}>
                      {label(s)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Priority
                <select name="priority" defaultValue={t.priority}>
                  {PRIORITIES.map((p) => (
                    <option key={p} value={p}>
                      {label(p)}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Assignment group
                <input name="assignment_group" defaultValue={t.assignment_group ?? ""} />
              </label>
            </div>
            <button type="submit">Save</button>
          </form>
        </section>
      )}

      <section className="card">
        <h2>Work notes ({t.work_notes.length})</h2>
        {t.work_notes.length === 0 && <p className="muted">No work notes yet.</p>}
        <ol className="notes">
          {t.work_notes.map((n, i) => (
            <li key={i}>
              <div className="muted">
                {n.author} · {formatDate(n.created_at)}
              </div>
              <p className="pre">{n.body}</p>
            </li>
          ))}
        </ol>
        {!closed && (
          <form action={note} className="form">
            <textarea name="body" required rows={3} placeholder="What did you check or try?" />
            <div className="row">
              <input name="author" required placeholder="Your name" aria-label="Your name" />
              <button type="submit">Add work note</button>
            </div>
          </form>
        )}
      </section>

      {!closed && !resolved && (
        <section className="card">
          <h2>Resolve</h2>
          <form action={resolve} className="form">
            <textarea
              name="resolution_notes"
              required
              minLength={10}
              rows={3}
              placeholder="What fixed it? This is what the AI agent will learn from."
            />
            <div className="row">
              <input name="resolved_by" required placeholder="Your name" aria-label="Your name" />
              <button type="submit">Resolve ticket</button>
            </div>
          </form>
        </section>
      )}
    </main>
  );
}
