import React, { useState } from "react";
import api from '../config/axiosConfig'
import { useNavigate } from "react-router-dom";
import '../css/LoginForm.css';

const LoginForm = () => {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    email: "",
    password: ""
  });

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // Handle input changes
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Handle login form submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      // Call backend login API
      const res = await api.post(
        "/api/auth/login",
        form,
        {
          headers: { "Content-Type": "application/json" }
        }
      );

      const { token, role } = res.data;
      console.log(res)

      if (!token || !role) {
        setError("Invalid backend response");
        return;
      }


      // Store JWT and role in sessionStorage
      sessionStorage.setItem("token", token);
      sessionStorage.setItem("role", role);

      // Redirect based on role
      if (role === "SUPERVISOR") navigate("/dashboard");
     

    } catch (err) {
      console.log(err)
       if (!err.response) {
    setError("Server is under maintainance. Please try again later.");
  } else if (err.response.status === 401) {
   setError("Invalid username or password");
  } else {
    alert("Something went wrong. Please try again.");
  }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h2>Login</h2>

        <input
          type="text"
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          required
        />

        <input
          type="password"
          name="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
          required
        />

        <button type="submit" disabled={isLoading}>
          {isLoading ? <span className="button-loader" aria-hidden="true"></span> : "Login"}
        </button>
        <a href="/forgetpass">Forgot Password ?</a> <a href="/signup">Not a user</a>

        {error && <p style={{ color: "red", marginTop: "10px" }}>{error}</p>}
      </form>
    </div>
  );
};

export default LoginForm;
