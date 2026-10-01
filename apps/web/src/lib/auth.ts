/** Client-side auth token helpers.

Prefer HttpOnly cookies set by the API (VAPT: tokens must not live in localStorage).
Bearer tokens in memory remain as a fallback for same-tab API calls and legacy clients.
*/
const ACCESS_TOKEN_KEY = "erp_access_token";
const REFRESH_TOKEN_KEY = "erp_refresh_token";

let memoryAccessToken: string | null = null;
let memoryRefreshToken: string | null = null;

function purgeLegacyWebStorage(): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_KEY);
    window.sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    window.sessionStorage.removeItem(REFRESH_TOKEN_KEY);
  } catch {
    // ignore quota / privacy mode
  }
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  if (memoryAccessToken) return memoryAccessToken;
  // Migrate once from legacy localStorage, then purge.
  const legacy = window.localStorage.getItem(ACCESS_TOKEN_KEY);
  if (legacy) {
    memoryAccessToken = legacy;
    purgeLegacyWebStorage();
    return legacy;
  }
  return null;
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  if (memoryRefreshToken) return memoryRefreshToken;
  const legacy = window.localStorage.getItem(REFRESH_TOKEN_KEY);
  if (legacy) {
    memoryRefreshToken = legacy;
    purgeLegacyWebStorage();
    return legacy;
  }
  // Refresh may exist only as HttpOnly cookie — return null; refresh endpoint reads cookie.
  return null;
}

export function setTokens(accessToken: string, refreshToken?: string) {
  memoryAccessToken = accessToken;
  if (refreshToken) {
    memoryRefreshToken = refreshToken;
  }
  purgeLegacyWebStorage();
}

export function clearTokens() {
  memoryAccessToken = null;
  memoryRefreshToken = null;
  purgeLegacyWebStorage();
}

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken());
}

/** Send user to login with return URL (client-only). */
export function redirectToLogin(): void {
  if (typeof window === "undefined") return;
  const path = window.location.pathname;
  if (path.startsWith("/login") || path.startsWith("/onboarding")) return;
  const next = `${path}${window.location.search}`;
  window.location.assign(`/login?next=${encodeURIComponent(next)}`);
}

/** Best-effort JWT `sub` for UI-only checks (SoD hints). Not a security boundary. */
export function getAccessTokenUserId(): string | null {
  const token = getAccessToken();
  if (!token) return null;
  const parts = token.split(".");
  if (parts.length < 2) return null;
  try {
    const payload = JSON.parse(atob(parts[1].replace(/-/g, "+").replace(/_/g, "/"))) as {
      sub?: string;
    };
    return payload.sub ?? null;
  } catch {
    return null;
  }
}
