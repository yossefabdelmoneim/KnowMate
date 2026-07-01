const API_BASE = "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

function getToken(): string | null {
  return localStorage.getItem("knowmate_token");
}

export function setToken(token: string | null) {
  if (token) {
    localStorage.setItem("knowmate_token", token);
  } else {
    localStorage.removeItem("knowmate_token");
  }
}

function getCachedUser(): unknown | null {
  try {
    const raw = localStorage.getItem("knowmate_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setCachedUser(user: unknown | null) {
  if (user) {
    localStorage.setItem("knowmate_user", JSON.stringify(user));
  } else {
    localStorage.removeItem("knowmate_user");
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  auth = true
): Promise<T> {
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] ?? "application/json";
  }

  if (auth) {
    const token = getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    let detail = `Request failed with status ${res.status}`;
    try {
      const body = await res.json();
      if (Array.isArray(body.detail)) {
        detail = body.detail.map((e: { msg: string }) => e.msg).join("; ");
      } else {
        detail = body.detail ?? body.message ?? detail;
      }
    } catch {
      // ignore parse errors
    }
    throw new ApiError(detail, res.status);
  }

  if (res.status === 204) return undefined as T;

  return res.json();
}

export const api = {
  get: <T>(path: string, auth = true) => request<T>(path, { method: "GET" }, auth),
  post: <T>(path: string, body?: unknown, auth = true) =>
    request<T>(path, { method: "POST", body: body ? JSON.stringify(body) : undefined }, auth),
  postForm: <T>(path: string, formData: FormData, auth = true) =>
    request<T>(path, { method: "POST", body: formData }, auth),
  patch: <T>(path: string, body?: unknown, auth = true) =>
    request<T>(path, { method: "PATCH", body: body ? JSON.stringify(body) : undefined }, auth),
  delete: <T>(path: string, auth = true) => request<T>(path, { method: "DELETE" }, auth),
  getToken,
  setToken,
  getCachedUser,
  setCachedUser,
};
