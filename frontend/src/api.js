// Base URL of the FastAPI backend.
//
// Vite inlines VITE_API_URL at BUILD time. A real process env var wins over
// the .env file, so setting it in the host's dashboard overrides
// .env.production. Whichever way it is set, the value must be resolved now:
// changing it later requires a rebuild, not just a redeploy.
const configuredUrl = import.meta.env.VITE_API_URL;

export const API_URL = configuredUrl || "http://127.0.0.1:8000";

if (import.meta.env.PROD && API_URL === "http://127.0.0.1:8000") {
  // Silently shipping a production bundle that points at localhost looks
  // like a backend outage: every request fails, but nothing explains why.
  console.error(
    "[api] VITE_API_URL was not set at build time. This bundle is calling " +
      `${API_URL} (this machine's own backend). Set VITE_API_URL before ` +
      "building, then rebuild and redeploy."
  );
}
