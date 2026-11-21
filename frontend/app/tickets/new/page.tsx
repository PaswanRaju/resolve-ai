import Link from "next/link";

import { label, PRIORITIES } from "@/lib/api";

import { createTicket } from "../actions";

export default function NewTicketPage() {
  return (
    <main className="container">
      <p>
        <Link href="/tickets">← All tickets</Link>
      </p>
      <h1>New ticket</h1>
      <form action={createTicket} className="card form">
        <label>
          Short description
          <input name="short_description" required minLength={5} maxLength={160} />
        </label>
        <label>
          Description
          <textarea name="description" required rows={5} />
        </label>
        <div className="row">
          <label>
            Category
            <input name="category" placeholder="network, email, hardware..." />
          </label>
          <label>
            Priority
            <select name="priority" defaultValue="3-moderate">
              {PRIORITIES.map((p) => (
                <option key={p} value={p}>
                  {label(p)}
                </option>
              ))}
            </select>
          </label>
        </div>
        <label>
          Caller
          <input name="caller" required placeholder="Who is reporting this?" />
        </label>
        <button type="submit">Create ticket</button>
      </form>
    </main>
  );
}
