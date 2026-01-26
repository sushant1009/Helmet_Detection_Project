import React, { useState, useEffect } from "react";
import { Navigate } from "react-router-dom";

const PrivateRoute = ({ children, allowedRoles }) => {
  const [auth, setAuth] = useState({
    token: sessionStorage.getItem("token"),
    role: sessionStorage.getItem("role"),
  });

  useEffect(() => {
    const handleStorageChange = () => {
      setAuth({
        token: sessionStorage.getItem("token"),
        role: sessionStorage.getItem("role"),
      });
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  if (!auth.token) return <Navigate to="/login" />;

  if (allowedRoles && !allowedRoles.includes(auth.role)) return <Navigate to="/login" />;

  return children;
};

export default PrivateRoute;
