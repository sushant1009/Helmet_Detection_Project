import { React, useEffect, useState } from "react";
import { NavLink,Link, useNavigate } from "react-router-dom";
import { Home, UserPlus, Play, Table, Camera, LogIn, LogOut } from "lucide-react";
import LoadingButton from "./LoadingButton";
import "../css/Sidebar.css";

function parseJwtExpiry(token) {
  try {
    const payload = token.split(".")[1];
    if (!payload) return null;
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = normalized + "=".repeat((4 - (normalized.length % 4)) % 4);
    const decoded = JSON.parse(atob(padded));
    return typeof decoded.exp === "number" ? decoded.exp * 1000 : null;
  } catch {
    return null;
  }
}

function formatRemaining(ms) {
  if (ms <= 0) return "00:00:00";
  const totalSeconds = Math.floor(ms / 1000);
  const hours = String(Math.floor(totalSeconds / 3600)).padStart(2, "0");
  const minutes = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, "0");
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return `${hours}:${minutes}:${seconds}`;
}

export default function Sidebar() {
  const role = sessionStorage.getItem("role");
  const [open, setOpen] = useState(false);
  const [sessionRemaining, setSessionRemaining] = useState(null);
  const [sessionExpired, setSessionExpired] = useState(false);
  
    const logout = () => {
      sessionStorage.clear();
      navigate("/login");
    };
   const navigate = useNavigate();

  useEffect(() => {
    const token = sessionStorage.getItem("token");
    if (!token) {
      setSessionRemaining(null);
      setSessionExpired(false);
      return;
    }

    const expiryMs = parseJwtExpiry(token);
    if (!expiryMs) {
      setSessionRemaining(null);
      setSessionExpired(false);
      return;
    }

    const tick = () => {
      const remaining = expiryMs - Date.now();
      if (remaining <= 0) {
        setSessionRemaining("00:00:00");
        setSessionExpired(true);
        return;
      }
      setSessionRemaining(formatRemaining(remaining));
      setSessionExpired(false);
    };

    tick();
    const intervalId = setInterval(tick, 1000);
    return () => clearInterval(intervalId);
  }, [role]);

  return (
    <div className="sidebar">
      <h1 className="sidebar-title">
        <span className="sidebar-title-glow">VisionShield</span>
      </h1>
      {role && sessionRemaining && (
        <div className={`session-timer ${sessionExpired ? "expired" : ""}`}>
          <span className="session-label">Session</span>
          <span className="session-time">{sessionExpired ? "Expired" : sessionRemaining}</span>
        </div>
      )}
      <div>
              {!role && (
                <>
                  <NavLink to="/login" className="nav-item" ><LogIn/>Login</NavLink>
                  <NavLink to="/signup" className="nav-item" ><UserPlus/>Signup</NavLink>
                   <Link to="/forgetpass" ></Link>
                </>
              )}
        </div>
      
       {
    (role === "SUPERVISOR") &&
        (
          <nav>
        <NavLink to="/" className="nav-item"><Home /> Dashboard</NavLink>
        <NavLink to="/register" className="nav-item"><UserPlus /> Register</NavLink>
        <NavLink to="/attendance" className="nav-item"><Play /> Attendance</NavLink>
        <NavLink to="/helmet-monitoring" className="nav-item"><Camera/>Helmet Monitoring</NavLink>
        <NavLink to="/logs" className="nav-item"><Table /> Logs</NavLink>
        <LoadingButton className="logout-btn" onClick={logout}>
             <LogOut/> Logout
            </LoadingButton>
      </nav>
        )  
      }
    </div>
  );
}
