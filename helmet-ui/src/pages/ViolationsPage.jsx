import { useState } from "react";
import api from "../config/axiosConfig";
import '../css/Violations.css'

function ViolationsPage({ setActiveView }) {

  const [date, setDate] = useState("");
  const [data, setData] = useState([]);

  const fetchViolations = async () => {
    try {
      const res = await api.get(`/api/worker/violations/${date}`);
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
        <h2 className="violations-title">Violations</h2>
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
            <th>Worker Name</th>
            <th>Date</th>
            <th>Score</th>
            <th>Site</th>
            <th>Image</th>
          </tr>
        </thead>

        <tbody>
          {data.length > 0 ? (
            data.map((v, i) => (
              <tr key={i}>
                <td>{v.workerName}</td>
                <td>{v.date}</td>
                <td>{v.score}</td>
                <td>{v.siteName}</td>
                <td>
                  <img
                    src={v.filePath}
                    alt="violation"
                    className="violation-img"
                  />
                </td>
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

export default ViolationsPage;