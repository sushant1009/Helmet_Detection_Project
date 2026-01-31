import {React, useState} from "react";
import { NavLink,Link, useNavigate } from "react-router-dom";
import { Home, UserPlus, Play, Table, Camera, LogIn, LogOut } from "lucide-react";
import "../css/Sidebar.css";

export default function Sidebar() {
  const role = sessionStorage.getItem("role");
  const [open, setOpen] = useState(false);
  
    const logout = () => {
      sessionStorage.clear();
      navigate("/login");
    };
   const navigate = useNavigate();
  return (
    <div className="sidebar">
      <h1 className="sidebar-title">Helmet AI</h1>
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
        <button className="logout-btn" onClick={logout}>
             <LogOut/> Logout
            </button>
      </nav>
        )  
      }
    </div>
  );
}
