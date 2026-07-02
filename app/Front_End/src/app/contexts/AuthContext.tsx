import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";
import { login as loginApi, registerCompany as registerApi, getMe, logout as logoutApi, verifyCompany as verifyApi, getStoredUser, type User } from "../services/auth";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (companyName: string, firstName: string, lastName: string, email: string, password: string) => Promise<{ message: string; email: string }>;
  verify: (token: string) => Promise<{ message: string; company_name: string; admin_email: string }>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(getStoredUser);
  const token = localStorage.getItem("knowmate_token");
  const [loading, setLoading] = useState(!!token);

  useEffect(() => {
    if (token) {
      getMe().then((u) => {
        setUser(u);
        setLoading(false);
      });
    } else {
      setUser(null);
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const u = await loginApi(email, password);
    setUser(u);
    return u;
  }, []);

  const register = useCallback(async (companyName: string, firstName: string, lastName: string, email: string, password: string) => {
    return registerApi(companyName, firstName, lastName, email, password);
  }, []);

  const verify = useCallback(async (token: string) => {
    return verifyApi(token);
  }, []);

  const logout = useCallback(() => {
    logoutApi();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, verify, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
