import { useState } from "react";
import api from "../config/axiosConfig";
import '../css/Violations.css'

function AttendancePage({ setActiveView }) {

  const [date, setDate] = useState("");
  const [data, setData] = useState([]);

  const fetchViolations = async () => {
    try {
      const res = await api.get(`/api/attendance/${date}`);
      console.log(res.data)
      setData(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>

      {/* Header */}
      <div className="violations-header">
        <button className="back-btn" onClick={() => setActiveView("dashboard")}>
          ← Back
        </button>
        <h2 className="violations-title">Attendance</h2>
      </div>

      {/* Controls */}
      <div className="violations-controls">
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
        <button className="fetch-btn" onClick={fetchViolations}>
          Fetch
        </button>
      </div>

      {/* Table */}
      <table className="violations-table">
        <thead>
          <tr>
            <th>Attendance Id</th>
            <th>Worker Id</th>
            <th>Date</th>
            <th>Entry Time</th>
            <th>Exit Time</th>
          </tr>
        </thead>

        <tbody>
          {data.length > 0 ? (
            data.map((a, i) => (
              <tr key={i}>
                <td>{a.attendanceId}</td>
                <td>{a.workerId}</td>
                <td>{a.date}</td>
                <td>{a.entryTime}</td>
                <td>{a.exitTime}</td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="5" className="no-data">
                No Data Found
              </td>
            </tr>
          )}
        </tbody>

      </table>
    </div>
  );
}

export default AttendancePage;