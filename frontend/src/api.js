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

// An error carrying a message that is safe to show a user.
export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status ?? null;
  }
}

// When a response fails at the network layer, the browser deliberately hides
// the status code -- it reports "blocked by CORS policy" even when the real
// problem is a gateway 502 from a server that ran out of memory or restarted.
// The origin check and the server error get conflated, so a server crash
// looks like a frontend bug. There is no way to recover the true status from
// here, so say that plainly instead of surfacing "Failed to fetch".
const UNREACHABLE_MESSAGE =
  "Could not reach the server. It may be restarting, or the request " +
  "exceeded its time limit. If this keeps happening the backend may have " +
  "run out of memory.";

const GATEWAY_MESSAGES = {
  502: "The server is not responding correctly (502). It most likely ran " +
       "out of memory or crashed. Check the backend logs.",
  503: "The service is unavailable (503), usually while it restarts. " +
       "Please try again shortly.",
  504: "The server took too long to respond (504). It may have run out " +
       "of memory.",
};

/**
 * fetch() with error messages that name the actual failure.
 *
 * Throws ApiError on any non-2xx response or network failure.
 */
export async function apiFetch(path, options = {}) {
  let response;

  try {
    response = await fetch(`${API_URL}${path}`, options);
  } catch {
    // No response at all: DNS, TLS, connection refused, or a response the
    // browser refused to hand over because it lacked CORS headers.
    throw new ApiError(UNREACHABLE_MESSAGE);
  }

  if (response.ok) {
    // A gateway error page can arrive with a 200, so still guard the parse.
    try {
      return await response.json();
    } catch {
      throw new ApiError(
        `The server returned a response that was not valid JSON ` +
          `(status ${response.status}).`,
        response.status
      );
    }
  }

  // Prefer the API's own message; fall back to a status-specific one.
  let detail = null;
  try {
    const body = await response.json();
    detail = typeof body?.detail === "string" ? body.detail : null;
  } catch {
    // Non-JSON error body -- e.g. the HTML error page from a proxy.
  }

  throw new ApiError(
    detail ||
      GATEWAY_MESSAGES[response.status] ||
      `Request failed with status ${response.status}.`,
    response.status
  );
}