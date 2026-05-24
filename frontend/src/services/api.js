import axios from "axios";
import { getToken, logout } from "./auth";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

console.log("API URL:", API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add token to every request
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle unauthorized globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      logout();
    }
    return Promise.reject(error);
  }
);

// AUTH APIs
export const signupApi = async (fullName, email, password, confirmPassword) => {
  const response = await api.post("/api/auth/signup", {
    full_name: fullName,
    email,
    password,
    confirm_password: confirmPassword,
  });
  return response.data;
};

export const loginApi = async (email, password) => {
  const response = await api.post("/api/auth/login", {
    email,
    password,
  });
  return response.data;
};

// TENDER APIs
export const uploadTender = async (file, title) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("title", title);

  const response = await api.post("/api/tender/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

// BIDDER APIs
export const uploadBidderDocuments = async (files, bidderName, tenderId) => {
  const formData = new FormData();

  files.forEach((file) => formData.append("files", file));
  formData.append("bidder_name", bidderName);
  formData.append("tender_id", tenderId);

  const response = await api.post("/api/bidder/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

// EVALUATION APIs
export const evaluateBidders = async (tenderId, bidderIds) => {
  const response = await api.post("/api/evaluation/evaluate", {
    tender_id: tenderId,
    bidder_ids: bidderIds,
  });

  return response.data;
};

// REPORT DOWNLOAD API
export const downloadEvaluationReport = async (tenderId) => {
  const response = await api.get(`/api/evaluation/report/${tenderId}/download`, {
    responseType: "blob",
  });

  const blob = new Blob([response.data], { type: "text/plain" });
  const url = window.URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = `tender_evaluation_report_${tenderId}.txt`;

  document.body.appendChild(link);
  link.click();

  link.remove();
  window.URL.revokeObjectURL(url);
};

export default api;