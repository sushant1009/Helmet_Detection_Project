import { React, useState, useEffect } from "react";
import axios from "axios";
import api from '../config/axiosConfig';
import "../css/Forgetpass.css";

const RESEND_TIME = 60; // seconds

const Forgetpass = () => {
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [otpVerified, setOtpVerified] = useState(false);
  const [message, setMessage] = useState("");
  const [timer, setTimer] = useState(RESEND_TIME);
  const [canResend, setCanResend] = useState(false);

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // Countdown timer for resend OTP
  useEffect(() => {
    let interval;

    if (otpSent && timer > 0) {
      interval = setInterval(() => setTimer((prev) => prev - 1), 1000);
    }

    if (timer === 0) {
      setCanResend(true);
      clearInterval(interval);
    }

    return () => clearInterval(interval);
  }, [otpSent, timer]);

  const validateEmail = (value) =>{
     if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value))
     {
        setMessage("Invalid email format")
        return false
     }else{
      
      return true
     }
         
  }

  // Send OTP
  const sendOtp = async () => {
    if(validateEmail(email))
    {
      try {
      await api.post("/api/auth/otp/send", null, { params: { email } });
      setOtpSent(true);
      setTimer(RESEND_TIME);
      setCanResend(false);
      setMessage("OTP sent to your email");
    } catch(error) {
      console.log(error.response?.status)
    if (error.response?.status === 404) {
      setMessage("Email Not Found");
    }else if (error.response?.status === 500) {
      setMessage("Internal Server Error");
    }  else{
      setMessage("OTP verification failed");
    }
      
    }
    }
    
  };

  // Verify OTP
  const verifyOtp = async () => {
    try {
      await api.post("/api/auth/otp/verify", null, { params: { email, otp } });
      setMessage("OTP verified successfully ");
      setOtpVerified(true);
    } catch {
       if (error.response?.status === 400) {
      setMessage("Invalid or expired OTP ");
    } else if (error.response?.status === 401) {
      setMessage("Invalid Credentials ");
    }else if (error.response?.status === 403) {
      setMessage("Invalid or expired OTP");
    }else if (error.response?.status === 500) {
      setMessage("Internal Server Error");
    }  else{
      setMessage("OTP verification failed");
    }
      setOtpVerified(false);
    }
  };

  // Change Password after OTP verification
  const changePassword = async () => {
    if (newPassword !== confirmPassword) {
      setMessage("Passwords do not match ");
      return;
    }

    try {
      await api.put("/api/auth/change-pass", null, {
        params: { email, newPassword },
      });
      setMessage("Password changed successfully ");
      // Optional: Reset state
      setEmail("");
      setOtp("");
      setOtpSent(false);
      setOtpVerified(false);
      setNewPassword("");
      setConfirmPassword("");
    } catch {
       if (error.response?.status === 400) {
      setMessage("Invalid or expired OTP ");
    } else if (error.response?.status === 401) {
      setMessage("Invalid Credentials ");
    }else if (error.response?.status === 403) {
      setMessage("Expired or Unverified OTP ");
    }else if (error.response?.status === 500) {
      setMessage("Internal Server Error");
    }  else{
      setMessage("OTP verification failed");
    }
    }
  };

  return (
    <div className="otp-container">
      <h2>Reset Password</h2>

      {/* Email input */}
      <input
        type="email"
        placeholder="Enter your email"
        value={email}
        onChange={(e)=>setEmail(e.target.value)}
        disabled={otpSent || otpVerified}
        required
    
      />

      {/* Send OTP button */}
      {!otpSent && <button onClick={sendOtp}>Send OTP</button>}

      {/* OTP verification section */}
      {otpSent && !otpVerified && (
        <>
        <p>OTP sent to</p><strong> {email}</strong>
          <input
            type="text"
            placeholder="Enter OTP"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
          />
          <button onClick={verifyOtp}>Verify OTP</button>

          {!canResend ? (
            <p className="timer">
              Resend OTP in <strong>{timer}s</strong>
            </p>
          ) : (
            <button className="resend-btn" onClick={sendOtp}>
              Resend OTP
            </button>
          )}
        </>
      )}

      {/* Change password section after OTP verification */}
      {otpVerified && (
        <>
          <input
            type="password"
            placeholder="New Password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            
          />
          <input
            type="password"
            placeholder="Confirm Password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
          <button onClick={changePassword}>Change Password</button>
        </>
      )}

      {/* Message display */}
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default Forgetpass;
