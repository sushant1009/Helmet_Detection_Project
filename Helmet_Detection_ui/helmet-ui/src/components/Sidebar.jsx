import React from "react";
import { NavLink } from "react-router-dom";
import { Home, UserPlus, Play, Table, Camera } from "lucide-react";
import "./Sidebar.css";

export default function Sidebar() {
  return (
    <div className="sidebar">
      <h1 className="sidebar-title">Helmet AI</h1>
      <nav>
        <NavLink to="/" className="nav-item"><Home /> Dashboard</NavLink>
        <NavLink to="/register" className="nav-item"><UserPlus /> Register</NavLink>
        <NavLink to="/attendance" className="nav-item"><Play /> Attendance</NavLink>
        <NavLink to="/helmet-monitoring" className="nav-item"><Camera/>Helmet Monitoring</NavLink>
        <NavLink to="/logs" className="nav-item"><Table /> Logs</NavLink>
      </nav>
    </div>
  );
}
