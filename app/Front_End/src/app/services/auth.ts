import { api } from "./api";

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  company_id: number | null;
  role: string;
  created_at: string;
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface RegisterCompanyResponse {
  message: string;
  email: string;
}

interface AdminInfo {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}

export async function login(email: string, password: string): Promise<User> {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const res = await fetch("http://localhost:8000/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData,
  });

  if (!res.ok) {
    let detail = "Login failed";
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch { /* ignore */ }
    throw new Error(detail);
  }

  const data: LoginResponse = await res.json();
  api.setToken(data.access_token);

  const user = await api.get<User>("/auth/me");
  api.setCachedUser(user);
  return user;
}

export async function registerCompany(
  companyName: string,
  firstName: string,
  lastName: string,
  email: string,
  password: string
): Promise<RegisterCompanyResponse> {
  return api.post<RegisterCompanyResponse>("/companies/register", {
    company_name: companyName,
    admin: { first_name: firstName, last_name: lastName, email, password },
  }, false);
}

export async function verifyCompany(token: string) {
  return api.get<{ message: string; company_name: string; admin_email: string }>(
    `/companies/verify?token=${encodeURIComponent(token)}`,
    false
  );
}

export async function getMe(): Promise<User | null> {
  try {
    const user = await api.get<User>("/auth/me");
    api.setCachedUser(user);
    return user;
  } catch {
    api.setToken(null);
    api.setCachedUser(null);
    return null;
  }
}

export function logout() {
  api.setToken(null);
  api.setCachedUser(null);
}

export function getStoredUser(): User | null {
  return api.getCachedUser() as User | null;
}
