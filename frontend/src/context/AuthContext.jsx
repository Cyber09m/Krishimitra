import { createContext, useContext, useState, useCallback } from "react";
import client from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("km_user");
    return stored ? JSON.parse(stored) : null;
  });
  const [error, setError] = useState(null);

  const persist = (token, user) => {
    localStorage.setItem("km_token", token);
    localStorage.setItem("km_user", JSON.stringify(user));
    setUser(user);
  };

  const login = useCallback(async (email, password) => {
    setError(null);
    try {
      const { data } = await client.post("/auth/login", { email, password });
      persist(data.access_token, data.user);
      return true;
    } catch (err) {
      setError(err.response?.data?.error || "Login failed.");
      return false;
    }
  }, []);

  const register = useCallback(async (payload) => {
    setError(null);
    try {
      const { data } = await client.post("/auth/register", payload);
      persist(data.access_token, data.user);
      return true;
    } catch (err) {
      setError(err.response?.data?.error || "Registration failed.");
      return false;
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("km_token");
    localStorage.removeItem("km_user");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, setUser, login, register, logout, error }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
