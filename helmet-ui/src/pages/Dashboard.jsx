import { useState, useEffect } from "react";
import api from "../config/axiosConfig";
import ViolationsPage from "./ViolationsPage";
import AttendancePage from "./AttendancePage";
import RegisteredWorkers from "./RegisteredWorkers";
import '../css/Dashboard.css'

function Dashboard() {

  const [activeView, setActiveView] = useState("dashboard");

  const [dashboardData, setDashboardData] = useState({
    registeredWorkers: 0,
    attendance: 0,
    violations: 0
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const res = await api.get("/api/dashboard/stats");
        setDashboardData(res.data);
      } catch (error) {
        console.error(error);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <div className="d-flex">

      {/* Sidebar */}
      

      {/* MAIN CONTENT */}
      <div className="flex-grow-1 p-4">

        {activeView === "dashboard" && (
          <div>
            <h2 className="mb-4">Dashboard</h2>

            <div className="row">

              <div className="col-md-4">
                <div
                  className="card bg-dark text-white p-4"
                  style={{ cursor: "pointer" }}
                  onClick={() => setActiveView("workers")}
                >
                  <h4>Registered Workers</h4>
                  <p className="display-6">{dashboardData.registeredWorkers}</p>
                </div>
              </div>

              <div className="col-md-4">
                <div
                  className="card bg-dark text-white p-4"
                  style={{ cursor: "pointer" }}
                  onClick={() => setActiveView("attendance")}
                >
                  <h4>Today's Attendance</h4>
                  <p className="display-6 text-success">{dashboardData.attendance}</p>
                </div>
              </div>

              <div className="col-md-4">
                <div
                  className="card bg-dark text-white p-4"
                  style={{ cursor: "pointer" }}
                  onClick={() => setActiveView("violations")}
                >
                  <h4>Helmet Violations</h4>
                  <p className="display-6 text-danger">{dashboardData.violations}</p>
                </div>
              </div>

            </div>
          </div>
        )}

        {activeView === "violations" && <ViolationsPage />}

        {activeView === "attendance" && <AttendancePage/>}

        {activeView === "workers" && (
          <RegisteredWorkers/>
        )}

      </div>
    </div>
  );
}

export default Dashboard;