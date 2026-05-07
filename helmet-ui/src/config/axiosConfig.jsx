import axios from "axios";

const api = axios.create({
  baseURL: "https://helmet-detection-backend-lye2.onrender.com",
  headers: {
    "Content-Type": "application/json"
  }
});

// 🔐 Attach JWT to every request
api.interceptors.request.use(
  (config) => {
    const token = sessionStorage.getItem("token"); // session-based
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
