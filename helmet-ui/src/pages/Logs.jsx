import React from "react";
import "./Logs.css";

export default function Logs() {
  const logs = [
    { name: "Amit", time: "09:02 AM", helmet: "Yes" },
    { name: "Ravi", time: "09:07 AM", helmet: "No" },
  ];

  return (
    <div className="logs-container">
      <h2>Attendance Logs</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th><th>Time</th><th>Helmet</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((row, i) => (
            <tr key={i}>
              <td>{row.name}</td>
              <td>{row.time}</td>
              <td className={row.helmet === "Yes" ? "helmet-yes" : "helmet-no"}>{row.helmet}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
