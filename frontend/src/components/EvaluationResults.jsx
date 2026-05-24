import { useState } from "react";
import { evaluateBidders, downloadEvaluationReport } from "../services/api";

function EvaluationResults({ tenderId, bidders, results, onEvaluated }) {
  const [loading, setLoading] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(false);
  const [error, setError] = useState("");
  const [evaluationData, setEvaluationData] = useState(results);
  const [expandedIndex, setExpandedIndex] = useState(null);

  const handleRunEvaluation = async () => {
    if (!bidders || bidders.length === 0) {
      setError("No bidders available for evaluation. Please upload bidders first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const bidderIds = bidders.map((b) => b.id);
      const data = await evaluateBidders(tenderId, bidderIds);

      setEvaluationData(data);

      if (onEvaluated) {
        onEvaluated(data);
      }
    } catch (err) {
      console.error("Evaluation error:", err);
      setError(err.response?.data?.detail || "Evaluation failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!tenderId) {
      setError("Tender ID missing. Cannot download report.");
      return;
    }

    setDownloadLoading(true);
    setError("");

    try {
      await downloadEvaluationReport(tenderId);
    } catch (err) {
      console.error("Report download error:", err);
      setError(
        err.response?.data?.detail ||
          "Report download failed. Please run evaluation first."
      );
    } finally {
      setDownloadLoading(false);
    }
  };

  if (!evaluationData) {
    return (
      <div>
        <h2>Run Evaluation</h2>
        <p className="subtext">
          Evaluate all uploaded bidders against extracted tender criteria.
        </p>

        {error && <div className="error">{error}</div>}

        <button
          className="btn primary"
          onClick={handleRunEvaluation}
          disabled={loading}
        >
          {loading ? "⏳ Evaluating..." : "🚀 Run Evaluation"}
        </button>
      </div>
    );
  }

  const resultList = evaluationData.results || [];

  const eligibleCount = resultList.filter(
    (r) => r.overall_status === "eligible"
  ).length;

  const notEligibleCount = resultList.filter(
    (r) => r.overall_status === "not_eligible"
  ).length;

  const reviewCount = resultList.filter(
    (r) => r.overall_status === "needs_review"
  ).length;

  return (
    <div>
      <div className="results-header-row">
        <div>
          <h2>Evaluation Results</h2>
          <p className="subtext">
            Bidder-wise eligibility decision with criterion-level reasoning.
          </p>
        </div>

        <button
          className="download-report-btn"
          onClick={handleDownloadReport}
          disabled={downloadLoading || resultList.length === 0}
        >
          {downloadLoading
            ? "Downloading..."
            : "📥 Download Consolidated Report"}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {resultList.length === 0 ? (
        <div className="empty-results-box">
          <h3>No Evaluation Results Found</h3>
          <p>
            No bidders were evaluated. Please go back, upload bidders, and run
            evaluation again.
          </p>

          <button
            className="btn primary"
            onClick={handleRunEvaluation}
            disabled={loading}
          >
            {loading ? "Evaluating..." : "Run Evaluation Again"}
          </button>
        </div>
      ) : (
        <>
          <div className="summary-grid">
            <div className="summary-box success">
              <h3>{eligibleCount}</h3>
              <p>Eligible</p>
            </div>

            <div className="summary-box danger">
              <h3>{notEligibleCount}</h3>
              <p>Not Eligible</p>
            </div>

            <div className="summary-box warning">
              <h3>{reviewCount}</h3>
              <p>Needs Review</p>
            </div>
          </div>

          {resultList.map((result, index) => (
            <div className="result-box" key={index}>
              <div
                className={`result-top ${result.overall_status}`}
                onClick={() =>
                  setExpandedIndex(expandedIndex === index ? null : index)
                }
              >
                <div>
                  <strong>{result.bidder_name}</strong>
                  <span className="inline-meta">
                    {result.criteria_met}/{result.total_criteria} met
                  </span>
                </div>

                <div>{expandedIndex === index ? "▲" : "▼"}</div>
              </div>

              {expandedIndex === index && (
                <div className="result-body">
                  <p className="summary-text">{result.summary}</p>

                  <table className="table">
                    <thead>
                      <tr>
                        <th>Status</th>
                        <th>Criterion</th>
                        <th>Category</th>
                        <th>Extracted Value</th>
                        <th>Confidence</th>
                        <th>Reasoning</th>
                      </tr>
                    </thead>

                    <tbody>
                      {(result.criterion_evaluations || []).map((item, idx) => (
                        <tr key={idx}>
                          <td>
                            <span className={`badge ${item.status}`}>
                              {item.status === "met"
                                ? "✅ Met"
                                : item.status === "not_met"
                                ? "❌ Not Met"
                                : "⚠️ Uncertain"}
                            </span>
                          </td>

                          <td>{item.criterion_text}</td>
                          <td>{item.category}</td>
                          <td>{item.extracted_value || "N/A"}</td>

                          <td>
                            {item.confidence
                              ? `${(item.confidence * 100).toFixed(0)}%`
                              : "N/A"}
                          </td>

                          <td>{item.reasoning || "No reasoning available"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ))}
        </>
      )}
    </div>
  );
}

export default EvaluationResults;