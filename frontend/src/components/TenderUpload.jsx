import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { uploadTender } from "../services/api";

function TenderUpload({ onUploaded, existingTender }) {
  const [title, setTitle] = useState(existingTender?.title || "");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setError("");
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles: 1,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "image/*": [".png", ".jpg", ".jpeg", ".tiff"],
    },
  });

  const handleUpload = async () => {
    if (!title.trim()) {
      setError("Please enter tender title");
      return;
    }
    if (!file) {
      setError("Please select a tender file");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await uploadTender(file, title);
      onUploaded(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Tender upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>📄 Upload Tender Document</h2>
      <p className="subtext">
        Upload a tender PDF/DOCX/Image. The AI will automatically extract eligibility criteria.
      </p>

      {existingTender && (
        <div className="success-msg">
          ✅ Tender already uploaded: <strong>{existingTender.title}</strong>
          <br />
          <small>You can upload a new one to replace it, or proceed to next step.</small>
        </div>
      )}

      <input
        className="input"
        type="text"
        placeholder="Enter tender title (e.g., KSRTC Electric Bus Tender)"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />

      <div {...getRootProps()} className={`dropzone ${isDragActive ? "active" : ""}`}>
        <input {...getInputProps()} />
        {file ? (
          <p>
            ✅ Selected: <strong>{file.name}</strong>
          </p>
        ) : (
          <div>
            <p style={{ fontSize: "36px", margin: "10px" }}>📁</p>
            <p>Drag & drop tender file here, or click to browse</p>
            <p style={{ color: "#999", fontSize: "12px" }}>Supports: PDF, DOCX, PNG, JPG</p>
          </div>
        )}
      </div>

      {error && <div className="error">❌ {error}</div>}

      <button className="btn primary" onClick={handleUpload} disabled={loading}>
        {loading ? "⏳ Processing... (may take 30-60 seconds)" : "🚀 Upload & Extract Criteria"}
      </button>
    </div>
  );
}

export default TenderUpload;