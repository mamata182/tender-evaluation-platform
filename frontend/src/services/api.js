import axios from "axios";

// Use environment variable for production, fallback to local
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

console.log("API URL:", API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
});

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

export const evaluateBidders = async (tenderId, bidderIds) => {
  const response = await api.post("/api/evaluation/evaluate", {
    tender_id: tenderId,
    bidder_ids: bidderIds,
  });
  return response.data;
};

export default api;