import React, { createContext, useState } from "react";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);

  // Login function
  const login = (userData) => {
    setUser(userData);
    localStorage.setItem("token", "dummy-token");
    localStorage.setItem("user", JSON.stringify(userData));
  };

  // Logout function
  const logout = () => {
    setUser(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  };

  // Register function
  const register = (userData) => {
    // In a real app, you'd call an API here
    console.log("Registering user:", userData);
    // For demo, we'll just log them in
    login(userData);
  };

  // Check for existing session on mount
  React.useEffect(() => {
    const token = localStorage.getItem("token");
    const savedUser = localStorage.getItem("user");
    
    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  return (
    <AuthContext.Provider value={{ 
      user, 
      loading, 
      login, 
      logout, 
      register,
      isAuthenticated: !!user 
    }}>
      {children}
    </AuthContext.Provider>
  );
};