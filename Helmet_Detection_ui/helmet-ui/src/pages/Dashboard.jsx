import { useState, useEffect } from "react";
import api from "../config/axiosConfig";

function Dashboard() {

  const [dashboardData, setDashboardData] = useState({
    registeredWorkers: 0,
    attendance: 0,
    violations: 0
  });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const res = await api.get("/api/dashboard/stats");
        console.log(res.data);
        setDashboardData(res.data);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <div className="container mt-4">
      <h2 className="mb-4 text-center">Dashboard</h2>

      <div className="row">
        <div className="col-md-4">
          <div className="card text-center shadow-sm border-0 bg-dark text-white p-4">
            <h4>Registered Workers</h4>
            <p className="display-5 fw-bold mt-2">
              {dashboardData.registeredWorkers}
            </p>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card text-center shadow-sm border-0 bg-dark text-white p-4">
            <h4>Today's Attendance</h4>
            <p className="display-5 fw-bold mt-2 text-success">
              {dashboardData.attendance}
            </p>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card text-center shadow-sm border-0 bg-dark text-white p-4">
            <h4>Helmet Violations</h4>
            <p className="display-5 fw-bold mt-2 text-danger">
              {dashboardData.violations}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
