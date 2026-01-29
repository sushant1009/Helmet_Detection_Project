import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Link, useNavigate } from "react-router-dom";
import PrivateRoute from "./components/PrivateRoute";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Register from "./pages/Register";
import Attendance from "./pages/Attendance";
import HelmetMonitoring from "./pages/HelmetMonitoring";
import Forgetpass from "./pages/Forgetpass"
import SignupForm from "./pages/SignupForm"
import LoginForm from "./pages/LoginForm"
import Logs from "./pages/Logs";
import "./App.css";

export default function App() {
 
  return (
    
    <Router>
      <div className="app-container">
        <Sidebar />
        <div className="main-content">
          
          <Routes>
            <Route path="/login" element={<LoginForm />} />
          <Route path="/signup" element={<SignupForm />} />
          <Route path="/forgetpass" element={<Forgetpass />} />
          <Route
            path="/"
            element={
              <PrivateRoute allowedRoles={["SUPERVISOR"]}>
               <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute allowedRoles={["SUPERVISOR"]}>
               <Dashboard />
              </PrivateRoute>
            }
          />
          
            <Route path="/register" element={<PrivateRoute allowedRoles={["SUPERVISOR"]}>
               <Register />
              </PrivateRoute>} />
            <Route path="/attendance" element={<PrivateRoute allowedRoles={["SUPERVISOR"]}>
               <Attendance/>
              </PrivateRoute>} />
            <Route path="/helmet-monitoring" element={<PrivateRoute allowedRoles={["SUPERVISOR"]}>
               <HelmetMonitoring/>
              </PrivateRoute>} />
            <Route path="/logs" element={<PrivateRoute allowedRoles={["SUPERVISOR"]}>
               <Logs/>
              </PrivateRoute>} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}
