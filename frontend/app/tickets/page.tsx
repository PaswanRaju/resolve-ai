import Link from "next/link";

import { api, formatDate, label, STATUSES, type TicketList } from "@/lib/api";

export const dynamic = "force-dynamic";

type Props = { searchParams: Promise<{ status?: string; q?: string; page?: string }> };

const PAGE_SIZE = 20;

export default async function TicketsPage({ searchParams }: Props) {
  const { status = "", q = "", page = "1" } = await searchParams;
  const pageNum = Math.max(1, Number(page) || 1);

  const params = new URLSearchParams({
    limit: String(PAGE_SIZE),
    skip: String((pageNum - 1) * PAGE_SIZE),
  });
  if (status) params.set("status", status);
  if (q) params.set("q", q);
  const data = await api<TicketList>(`/tickets?${params}`);

  const pageLink = (n: number) => {
    const p = new URLSearchParams(params);
    p.delete("limit");
    p.delete("skip");
    p.set("page", String(n));
    return `/tickets?${p}`;
  };
  const lastPage = Math.max(1, Math.ceil(data.total / PAGE_SIZE));

  return (
    <main className="container wide">
      <div className="page-head">
        <h1>Tickets</h1>
        <Link className="button" href="/tickets/new">
          New ticket
        </Link>
      </div>

      {/* A plain GET form: filters live in the URL, so they can be bookmarked and shared. */}
      <form className="filters" method="get">
        <input name="q" placeholder="Search tickets" defaultValue={q} aria-label="Search" />
        <select name="status" defaultValue={status} aria-label="Status">
          <option value="">All statuses</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {label(s)}
            </option>
          ))}
        </select>
        <button type="submit">Filter</button>
      </form>

      {data.items.length === 0 ? (
        <p className="muted">No tickets found.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Number</th>
                <th>Short description</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Opened</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((t) => (
                <tr key={t.number}>
                  <td>
                    <Link href={`/tickets/${t.number}`}>{t.number}</Link>
                  </td>
                  <td>{t.short_description}</td>
                  <td>
                    <span className={`pill p${t.priority[0]}`}>{label(t.priority)}</span>
                  </td>
                  <td>
                    <span className={`pill s-${t.status}`}>{label(t.status)}</span>
                  </td>
                  <td className="muted">{formatDate(t.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="pager">
        <span className="muted">
          {data.total} ticket{data.total === 1 ? "" : "s"} · page {pageNum} of {lastPage}
        </span>
        {pageNum > 1 && <Link href={pageLink(pageNum - 1)}>Previous</Link>}
        {pageNum < lastPage && <Link href={pageLink(pageNum + 1)}>Next</Link>}
      </div>
    </main>
  );
}
