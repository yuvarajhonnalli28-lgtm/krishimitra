import React, { createContext, useState, useEffect, useContext } from "react";

// Create Theme Context
export const ThemeContext = createContext();

// Custom hook to use theme context
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  // Check if user has a theme preference in localStorage
  const getInitialTheme = () => {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme) {
      return savedTheme === "dark";
    }
    // Check system preference
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  };

  const [isDarkMode, setIsDarkMode] = useState(getInitialTheme);

  // Apply theme to document body
  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.add("dark-theme");
      document.body.classList.remove("light-theme");
      localStorage.setItem("theme", "dark");
    } else {
      document.body.classList.add("light-theme");
      document.body.classList.remove("dark-theme");
      localStorage.setItem("theme", "light");
    }
  }, [isDarkMode]);

  // Toggle theme function
  const toggleTheme = () => {
    setIsDarkMode(prev => !prev);
  };

  // Set specific theme
  const setTheme = (mode) => {
    setIsDarkMode(mode === "dark");
  };

  // Theme values to be provided
  const themeValues = {
    isDarkMode,
    toggleTheme,
    setTheme,
    colors: isDarkMode ? darkColors : lightColors
  };

  return (
    <ThemeContext.Provider value={themeValues}>
      {children}
    </ThemeContext.Provider>
  );
};

// Color palettes for light and dark themes
const lightColors = {
  primary: "#2e7d32",
  primaryDark: "#1b5e20",
  primaryLight: "#4caf50",
  secondary: "#ff8f00",
  background: "#f5f9f5",
  surface: "#ffffff",
  text: "#263238",
  textSecondary: "#546e7a",
  border: "#e0e0e0",
  error: "#d32f2f",
  success: "#388e3c",
  warning: "#ffa000",
  info: "#1976d2",
  card: "#ffffff",
  shadow: "rgba(0, 0, 0, 0.1)"
};

const darkColors = {
  primary: "#66bb6a",
  primaryDark: "#4caf50",
  primaryLight: "#81c784",
  secondary: "#ffb74d",
  background: "#121212",
  surface: "#1e1e1e",
  text: "#eceff1",
  textSecondary: "#b0bec5",
  border: "#37474f",
  error: "#ef5350",
  success: "#66bb6a",
  warning: "#ffb74d",
  info: "#42a5f5",
  card: "#2d2d2d",
  shadow: "rgba(0, 0, 0, 0.3)"
};