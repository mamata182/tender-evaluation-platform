import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { getUser, logout } from "../services/auth";
import TenderUpload from "../components/TenderUpload";
import CriteriaDisplay from "../components/CriteriaDisplay";
import BidderUpload from "../components/BidderUpload";
import EvaluationResults from "../components/EvaluationResults";

function TenderWorkflow() {
  const navigate = useNavigate();
  const user = getUser();

  const [step, setStep] = useState(1);
  const [tenderData, setTenderData] = useState(null);
  const [bidders, setBidders] = useState([]);
  const [evaluationResults, setEvaluationResults] = useState(null);
  const [completedSteps, setCompletedSteps] = useState({
    1: false, 2: false, 3: false, 4: false,
  });

  const handleTenderUploaded = (data) => {
    setTenderData(data);
    setCompletedSteps((prev) => ({ ...prev, 1: true }));
    setStep(2);
  };

  const handleCriteriaNext = () => {
    setCompletedSteps((prev) => ({ ...prev, 2: true }));
    setStep(3);
  };

  const handleBidderAdded = (bidder) => {
    setBidders((prev) => [...prev, bidder]);
    setCompletedSteps((prev) => ({ ...prev, 3: true }));
  };

  const handleGoToEvaluation = () => setStep(4);

  const handleEvaluationDone = (results) => {
    setEvaluationResults(results);
    setCompletedSteps((prev) => ({ ...prev, 4: true }));
  };

  const handleReset = () => {
    if (window.confirm("Start over? All uploaded data will be cleared.")) {
      setStep(1);
      setTenderData(null);
      setBidders([]);
      setEvaluationResults(null);
      setCompletedSteps({ 1: false, 2: false, 3: false, 4: false });
    }
  };

  const canAccessStep = (s) => {
    if (s === 1) return true;
    if (s === 2) return tenderData !== null;
    if (s === 3) return tenderData !== null;
    if (s === 4) return tenderData !== null && bidders.length > 0;
    return false;
  };

  const handleStepClick = (s) => {
    if (canAccessStep(s)) setStep(s);
  };

  return (
    <div className="app">
      <nav className="dashboard-nav">
        <div className="dashboard-logo">🏛️ TenderAI</div>
        <div className="dashboard-nav-right">
          <button className="back-btn" onClick={() => navigate("/dashboard")}>
            ← Dashboard
          </button>
          <span className="user-greeting">👤 {user?.full_name}</span>
          <button className="logout-btn" onClick={logout}>Logout</button>
        </div>
      </nav>

      <div style={{ maxWidth: "1100px", margin: "0 auto", padding: "20px" }}>
        <div className="stepper">
          {["Upload Tender", "Review Criteria", "Upload Bidders", "Evaluation"].map(
            (label, index) => {
              const s = index + 1;
              return (
                <div
                  key={s}
                  className={`step ${step === s ? "active" : ""} ${
                    completedSteps[s] ? "completed" : ""
                  } ${canAccessStep(s) ? "clickable" : "disabled"}`}
                  onClick={() => handleStepClick(s)}
                >
                  <span className="step-number">
                    {completedSteps[s] ? "✓" : s}
                  </span>
                  <span className="step-name">{label}</span>
                </div>
              );
            }
          )}
        </div>

        <div className="status-bar">
          {tenderData && (
            <span className="status-chip success">📄 {tenderData.title}</span>
          )}
          {tenderData?.criteria && (
            <span className="status-chip info">
              📋 {tenderData.criteria.length} Criteria
            </span>
          )}
          {bidders.length > 0 && (
            <span className="status-chip info">👥 {bidders.length} Bidders</span>
          )}
          {(tenderData || bidders.length > 0) && (
            <button
              className="reset-btn-small"
              onClick={handleReset}
            >
              🔄 Reset
            </button>
          )}
        </div>

        <div className="card">
          {step === 1 && (
            <TenderUpload onUploaded={handleTenderUploaded} existingTender={tenderData} />
          )}
          {step === 2 && tenderData && (
            <CriteriaDisplay tender={tenderData} onNext={handleCriteriaNext} />
          )}
          {step === 3 && tenderData && (
            <BidderUpload
              tenderId={tenderData.id}
              bidders={bidders}
              onBidderAdded={handleBidderAdded}
              onNext={handleGoToEvaluation}
            />
          )}
          {step === 4 && tenderData && (
            <EvaluationResults
              tenderId={tenderData.id}
              bidders={bidders}
              results={evaluationResults}
              onEvaluated={handleEvaluationDone}
            />
          )}
        </div>

        <div className="navigation">
          <button className="nav-btn" onClick={() => step > 1 && setStep(step - 1)} disabled={step === 1}>
            ⬅️ Back
          </button>
          <span className="step-indicator">Step {step} of 4</span>
          <button className="nav-btn" onClick={() => step < 4 && canAccessStep(step + 1) && setStep(step + 1)} disabled={step === 4 || !canAccessStep(step + 1)}>
            Next ➡️
          </button>
        </div>
      </div>
    </div>
  );
}

export default TenderWorkflow;