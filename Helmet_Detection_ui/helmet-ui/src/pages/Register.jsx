import React, { useState, useRef } from "react";
import axios from "axios";
import Webcam from "react-webcam";
import "./Register.css";
import { validateForm } from "./validateForm";

export default function Register() {
  const webcamRef = useRef(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [otpSent, setOtpSent] = useState(false);
  const [otpVerified, setOtpVerified] = useState(false);
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  

  const [formData, setFormData] = useState({
    aadhar_no: "",
    full_name: "",
    dob: "",
    email: "",
    phone: "",
    role:"",
  });

  const [message, setMessage] = useState("");

  const captureImage = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setCapturedImage(imageSrc);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };
  
  const sendOtp = async () => {
    const validationErrors = validateForm(formData);
  setErrors(validationErrors);
    if (!formData.email) return setMessage("Please enter email first.");
    if(Object.keys(validationErrors).length === 0)
    {
    try {
      await axios.post("http://localhost:8001/send-otp", { email: formData.email });
      setOtpSent(true);
      setMessage("OTP sent to your email.");
    } catch {
      setMessage("Failed to send OTP. Try again.");
    }
    }
  };

  const verifyOtp = async () => {
    try {
      const res = await axios.post("http://localhost:8001/verify-otp", {
        email: formData.email,
        otp,
      });
      if (res.data.success) {
        setOtpVerified(true);
        setMessage("Email verified successfully!");
      } else {
        setMessage("Invalid OTP. Try again.");
      }
    } catch {
      setMessage("Error verifying OTP.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validateForm(formData);
    setErrors(validationErrors);
    if (!otpVerified) return setMessage("Please verify your email first.");
    if (!capturedImage) return setMessage("Please capture a face image.");
    if(capturedImage && otpVerified && Object.keys(validationErrors).length === 0 )
    {
    setLoading(true);
    const blob = await (await fetch(capturedImage)).blob();
    const imageFile = new File([blob], "face.jpg", { type: "image/jpeg" });

    const data = new FormData();
data.append("full_name", formData.full_name);
data.append("aadhar_no", formData.aadhar_no);
data.append("dob", formData.dob);
data.append("email", formData.email);
data.append("phone", formData.phone);
data.append("role", formData.role);
data.append("file", imageFile);

    try {
      const res = await axios.post("http://localhost:8001/register", data);
      alert(res.data.message);
      setFormData({
    aadhar_no: "",
    full_name: "",
    dob: "",
    email: "",
    phone: "",
    role:"",
  })
  setCapturedImage(null)
  setOtpSent(false)
  setOtpVerified(false)
    } catch (err) {
      setMessage("Error registering user.");
      console.error(err);
    } finally {
      setLoading(false);
    }
    }
  };

  return (
    <div className="register-container container mt-4">
      <h2 className="text-center mb-4">Worker Registration</h2>

      <form className="register-form" onSubmit={handleSubmit}>
        <div className="row">
          {/* Aadhar Number */}
          <div className="col-md-6 mb-3">
            <input
              type="text"
              name="aadhar_no"
              placeholder="Aadhar Number"
              onChange={handleChange}
              value={formData.aadhar_no}
              className="form-control"
              required
            />
            {errors.aadhar_no && <small className="text-danger">{errors.aadhar_no}</small>}
          </div>

          {/* Full Name */}
          <div className="col-md-6 mb-3">
            <input
              type="text"
              name="full_name"
              placeholder="Full Name"
              onChange={handleChange}
              value={formData.full_name}
              className="form-control"
              required
            />
            {errors.full_name && <small className="text-danger">{errors.full_name}</small>}
          </div>

          {/* Date of Birth */}
          <div className="col-md-6 mb-3">
            <input
              type="date"
              name="dob"
              onChange={handleChange}
              value={formData.dob}
              className="form-control"
              required
            />
            {errors.dob && <small className="text-danger">{errors.dob}</small>}
          </div>
          <div className="role" onChange={handleChange}>
          <select name="role" id="role">
            <option value="">-- Select Role --</option>
            <option value="worker">Worker</option>
            <option value="supervisor">Supervisor</option>
          </select>
    {errors.role && <small className="text-danger">{errors.role}</small>}
          </div>

          {/* Email */}
          <div className="col-md-6 mb-3">
            <input
              type="email"
              name="email"
              placeholder="Email Address"
              onChange={handleChange}
              value={formData.email}
              className="form-control"
              required
            />
            {errors.email && <small className="text-danger">{errors.email}</small>}
          </div>

          {/* Phone */}
          <div className="col-md-6 mb-3">
            <input
              type="text"
              name="phone"
              placeholder="Phone Number"
              onChange={handleChange}
              value={formData.phone}
              className="form-control"
              required
            />
            {errors.phone && <small className="text-danger">{errors.phone}</small>}
          </div>
        </div>

        {/* OTP Section */}
        {!otpSent ? (
          <button type="button" onClick={sendOtp} className="btn btn-primary mt-2">
            Send OTP
          </button>
        ) : !otpVerified ? (
          <div className="mt-3">
            <input
              type="text"
              placeholder="Enter OTP"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              className="form-control d-inline w-auto me-2"
            />
            <button type="button" onClick={verifyOtp} className="btn btn-success">
              Verify OTP
            </button>
          </div>
        ) : (
          <p className="text-success mt-2">Email Verified ✅</p>
        )}

        
        <div className="camera-section mt-4 text-center">
          {!capturedImage ? (
            <>
              <Webcam
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                width={320}
                height={240}
                videoConstraints={{ facingMode: "user" }}
              />
              <button type="button" onClick={captureImage} className="btn btn-info mt-2">
                Capture Photo
              </button>
            </>
          ) : (
            <div>
              <img
                src={capturedImage}
                alt="Captured"
                width="320"
                height="240"
                className="border"
              />
              <button
                type="button"
                onClick={() => setCapturedImage(null)}
                className="btn btn-warning mt-2"
              >
                Retake
              </button>
            </div>
          )}
        </div>

        <div className="text-center mt-4">
          <button type="submit" className="btn btn-success" disabled={loading}>
            {loading ? "Registering..." : "Register Worker"}
          </button>
        </div>
      </form>

      {message && <p className="mt-3 text-center text-info">{message}</p>}
    </div>
  );
}
