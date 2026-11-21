// Server component: runs on the Next.js server, so it can call the backend
// by its Docker service name without exposing that URL to the browser.
export const dynamic = "force-dynamic";

type Health = { status: string; checks: Record<string, string> };

async function getHealth(): Promise<Health | null> {
  const base = process.env.BACKEND_URL ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/health/ready`, { cache: "no-store" });
    return (await res.json()) as Health;
  } catch {
    return null;
  }
}

export default async function Home() {
  const health = await getHealth();
  const services = health ? { api: "ok", ...health.checks } : { api: "down" };

  return (
    <main className="container">
      <h1>Resolve AI</h1>
      <p className="tagline">
        IT ticket portal with an AI agent that finds similar resolved tickets and suggests cited
        fixes.
      </p>

      <section className="card">
        <h2>System status</h2>
        <ul className="status">
          {Object.entries(services).map(([name, state]) => (
            <li key={name}>
              <span className={`dot ${state === "ok" ? "ok" : "down"}`} />
              {name}: {state}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
