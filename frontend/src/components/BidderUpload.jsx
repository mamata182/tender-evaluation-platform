import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { uploadBidderDocuments } from "../services/api";

function BidderUpload({ tenderId, bidders, onBidderAdded, onNext }) {
  const [bidderName, setBidderName] = useState("");
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onDrop = useCallback((acceptedFiles) => {
    setFiles((prev) => [...prev, ...acceptedFiles]);
    setError("");
  }, []);

  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "image/*": [".png", ".jpg", ".jpeg", ".tiff"],
    },
  });

  const handleAddBidder = async () => {
    if (!bidderName.trim()) {
      setError("Please enter bidder/company name");
      return;
    }
    if (files.length === 0) {
      setError("Please upload bidder documents");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await uploadBidderDocuments(files, bidderName, tenderId);
      onBidderAdded(data);
      setBidderName("");
      setFiles([]);
    } catch (err) {
      setError(err.response?.data?.detail || "Bidder upload failed");
    } finally {
      setLoading(false);
    }
  };

  const removeFile = (index) => {
    setFiles((prev) => prev.filter((_, idx) => idx !== index));
  };

  return (
    <div>
      <h2>👥 Upload Bidder Documents</h2>
      <p className="subtext">
        Add bidder/company submission documents. Each bidder can have multiple files.
      </p>

      {bidders.length > 0 && (
        <div className="success-msg">
          ✅ {bidders.length} bidder{bidders.length > 1 ? "s" : ""} already added
        </div>
      )}

      <div
        style={{
          border: "2px solid #1976d2",
          borderRadius: "12px",
          padding: "20px",
          marginBottom: "20px",
          background: "#f8fbff",
        }}
      >
        <h3 style={{ marginTop: 0, color: "#1976d2" }}>➕ Add New Bidder</h3>

        <input
          className="input"
          type="text"
          placeholder="Enter bidder/company name (e.g., TATA Motors)"
          value={bidderName}
          onChange={(e) => setBidderName(e.target.value)}
        />

        <div {...getRootProps()} className="dropzone">
          <input {...getInputProps()} />
          <p style={{ fontSize: "24px", margin: "5px" }}>📎</p>
          <p>Drag & drop bidder files here, or click to browse</p>
          <p style={{ color: "#999", fontSize: "12px" }}>Multiple files supported</p>
        </div>

        {files.length > 0 && (
          <div className="file-list">
            <strong>Files to upload ({files.length}):</strong>
            <div>
              {files.map((file, index) => (
                <div key={index} className="file-chip">
                  📄 {file.name}
                  <span
                    onClick={() => removeFile(index)}
                    style={{
                      marginLeft: "8px",
                      cursor: "pointer",
                      color: "#c62828",
                      fontWeight: "bold",
                    }}
                  >
                    ✕
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {error && <div className="error">❌ {error}</div>}

        <button className="btn primary" onClick={handleAddBidder} disabled={loading}>
          {loading ? "⏳ Processing..." : "➕ Add Bidder"}
        </button>
      </div>

      {bidders.length > 0 && (
        <>
          <div className="section">
            <h3>📋 Added Bidders ({bidders.length})</h3>
            {bidders.map((bidder, index) => (
              <div key={index} className="bidder-card">
                <div>
                  <strong>👤 {bidder.name}</strong>
                  <p style={{ margin: "5px 0 0 0", color: "#666", fontSize: "13px" }}>
                    Status: <span style={{ color: "#2e7d32" }}>✅ Processed</span>
                  </p>
                </div>
                <span className="tag" style={{ background: "#e3f2fd", color: "#1565c0" }}>
                  Bidder #{index + 1}
                </span>
              </div>
            ))}
          </div>

          <button className="btn secondary" onClick={onNext}>
            🚀 Continue to Evaluation →
          </button>
        </>
      )}
    </div>
  );
}

export default BidderUpload;