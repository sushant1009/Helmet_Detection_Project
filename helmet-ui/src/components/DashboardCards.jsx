export default function DashboardCards({ setActiveView }) {
  return (
    <div className="row">

      <div className="col-md-4">
        <div
          className="card bg-dark text-white p-4"
          style={{ cursor: "pointer" }}
          onClick={() => setActiveView("violations")}
        >
          <h4>Helmet Violations</h4>
        </div>
      </div>

      <div className="col-md-4">
        <div
          className="card bg-dark text-white p-4"
          style={{ cursor: "pointer" }}
          onClick={() => setActiveView("attendance")}
        >
          <h4>Attendance</h4>
        </div>
      </div>

      <div className="col-md-4">
        <div
          className="card bg-dark text-white p-4"
          style={{ cursor: "pointer" }}
          onClick={() => setActiveView("workers")}
        >
          <h4>Workers</h4>
        </div>
      </div>

    </div>
  );
}