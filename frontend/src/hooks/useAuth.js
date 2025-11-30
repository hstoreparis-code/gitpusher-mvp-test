import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/config/constants";

export function useAuth() {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (!token) return;
    axios
      .get(`${API}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.removeItem("token");
        setToken(null);
      });
  }, [token]);

  const login = async (email, password) =>
    axios
      .post(`${API}/auth/login`, { email, password })
      .then((res) => {
        localStorage.setItem("token", res.data.access_token);
        setToken(res.data.access_token);
        return res;
      });

  const register = async (email, password, display_name) =>
    axios.post(`${API}/auth/register`, { email, password, display_name });

  const logout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setUser(null);
  };

  return { token, user, login, register, logout };
}
