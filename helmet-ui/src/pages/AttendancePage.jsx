import { useState } from "react";
import api from "../config/axiosConfig";
import LoadingButton from "../components/LoadingButton";
import '../css/Violations.css'

function AttendancePage({ setActiveView }) {

  const [date, setDate] = useState("");
  const [data, setData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchViolations = async () => {
    try {
      setIsLoading(true);
      const res = await api.get(`/api/attendance/${date}`);
      console.log(res.data)
      setData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>

      {/* Header */}
      <div className="violations-header">
        <LoadingButton className="back-btn" onClick={() => setActiveView("dashboard")}>
          ← Back
        </LoadingButton>
        <h2 className="violations-title">Attendance</h2>
      </div>

      {/* Controls */}
      <div className="violations-controls">
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
        <LoadingButton className="fetch-btn" onClick={fetchViolations} loading={isLoading} loaderVariant="dark">
          Fetch
        </LoadingButton>
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