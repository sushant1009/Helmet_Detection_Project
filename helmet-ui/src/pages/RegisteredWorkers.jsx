import { useEffect, useState } from "react";
import api from "../config/axiosConfig";
import '../css/Violations.css'

function RegisteredWorkers({ setActiveView }) {

  const [date, setDate] = useState("");
  const [data, setData] = useState([]);

 useEffect(()=> {const fetchWorkers = async () => {
    try {
      const res = await api.get(`/api/worker/`);
      console.log(res.data)
      setData(res.data);
    } catch (err) {
      console.error(err);
    }
  };
 fetchWorkers();
},[]) 

  return (
    <div>

      {/* Header */}
      <div className="violations-header">
        <button className="back-btn" onClick={() => setActiveView("dashboard")}>
          ← Back
        </button>
        <h2 className="violations-title">Attendance</h2>
      </div>

      

      {/* Table */}
      <table className="violations-table">
        <thead>
          <tr>
            
            <th>Worker Id</th>
            <th>Full Name</th>
            <th>Aadhar No</th>
            <th>Email</th>
            <th>Date of Birth</th>
            <th>Phone Number</th>
            <th>Status</th>
            <th>Supervisor Id</th>
          </tr>
        </thead>

        <tbody>
          {data.length > 0 ? (
            data.map((w, i) => (
              <tr key={i}>
               <td>{w.workerId}</td>
                <td>{w.fullName}</td>
                 <td>{w.aadharNo}</td>
                  <td>{w.email}</td>
                   <td>{w.dob}</td>
                    <td>{w.phoneNo}</td>
                     <td>{w.status}</td>
                      <td>{w.supervisor}</td>
                      <td>
                  <img
                    src={w.photoPath}
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

export default RegisteredWorkers;