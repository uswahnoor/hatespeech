import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { auth } from "@/lib/api";

interface User {
  id: string;
  name: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, userData: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = auth.getToken();
    if (token) {
      // In a real app, you'd validate the token with the server
      setIsLoading(false);
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = (token: string, userData: User) => {
    auth.login(token);
    setUser(userData);
  };

  const logout = () => {
    auth.logout();
    setUser(null);
  };

  const value = {
    user,
    isAuthenticated: auth.isAuthenticated(),
    isLoading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}