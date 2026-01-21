import React from "react";

function Dashboard() {
  return (
    <div className="container mt-4">
      <h2 className="mb-4 text-center">Dashboard</h2>

      <div className="row">
        <div className="col-md-4">
          <div className="card text-center shadow-sm border-0 bg-dark text-white p-4">
            <h4>Registered Workers</h4>
            <p className="display-5 fw-bold mt-2">0</p>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card text-center shadow-sm border-0 bg-dark text-white p-4">
            <h4>Today's Attendance</h4>
            <p className="display-5 fw-bold mt-2 text-success">0</p>
          </div>
        </div>

        <div className="col-md-4">
          <div className="card text-center shadow-sm border-0 bg-dark text-white p-4">
            <h4>Helmet Violations</h4>
            <p className="display-5 fw-bold mt-2 text-danger">0</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
