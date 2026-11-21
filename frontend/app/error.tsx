"use client";

// Shown when a page throws, for example when the backend is down or rejects a form.
export default function ErrorPage({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <main className="container">
      <h1>Something went wrong</h1>
      <p className="muted">{error.message || "The request failed."}</p>
      <button onClick={reset}>Try again</button>
    </main>
  );
}
