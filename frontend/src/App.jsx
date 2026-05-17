import { useState } from "react";
import "./App.css";
import TenderUpload from "./components/TenderUpload";
import CriteriaDisplay from "./components/CriteriaDisplay";
import BidderUpload from "./components/BidderUpload";
import EvaluationResults from "./components/EvaluationResults";

function App() {
  const [step, setStep] = useState(1);
  const [tenderData, setTenderData] = useState(null);
  const [bidders, setBidders] = useState([]);
  const [evaluationResults, setEvaluationResults] = useState(null);

  // Track which steps are completed
  const [completedSteps, setCompletedSteps] = useState({
    1: false,
    2: false,
    3: false,
    4: false,
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

  const handleGoToEvaluation = () => {
    setStep(4);
  };

  const handleEvaluationDone = (results) => {
    setEvaluationResults(results);
    setCompletedSteps((prev) => ({ ...prev, 4: true }));
  };

  const handleReset = () => {
    if (window.confirm("Are you sure you want to start over? All data will be lost.")) {
      setStep(1);
      setTenderData(null);
      setBidders([]);
      setEvaluationResults(null);
      setCompletedSteps({ 1: false, 2: false, 3: false, 4: false });
    }
  };

  // Check if a step is accessible
  const canAccessStep = (stepNumber) => {
    if (stepNumber === 1) return true;
    if (stepNumber === 2) return tenderData !== null;
    if (stepNumber === 3) return tenderData !== null;
    if (stepNumber === 4) return tenderData !== null && bidders.length > 0;
    return false;
  };

  const handleStepClick = (stepNumber) => {
    if (canAccessStep(stepNumber)) {
      setStep(stepNumber);
    } else {
      alert(`Please complete previous steps first to access Step ${stepNumber}`);
    }
  };

  const goBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const goNext = () => {
    if (step < 4 && canAccessStep(step + 1)) {
      setStep(step + 1);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div>
            <h1>🏛️ AI Tender Evaluation Platform</h1>
            <p>Government Tender Eligibility Analysis System</p>
          </div>
          {(tenderData || bidders.length > 0) && (
            <button className="reset-btn" onClick={handleReset}>
              🔄 Start Over
            </button>
          )}
        </div>
      </header>

      {/* Clickable Stepper */}
      <div className="stepper">
        <div
          className={`step ${step >= 1 ? "active" : ""} ${
            completedSteps[1] ? "completed" : ""
          } ${canAccessStep(1) ? "clickable" : "disabled"}`}
          onClick={() => handleStepClick(1)}
        >
          <span className="step-number">
            {completedSteps[1] ? "✓" : "1"}
          </span>
          <span className="step-name">Upload Tender</span>
        </div>

        <div
          className={`step ${step >= 2 ? "active" : ""} ${
            completedSteps[2] ? "completed" : ""
          } ${canAccessStep(2) ? "clickable" : "disabled"}`}
          onClick={() => handleStepClick(2)}
        >
          <span className="step-number">
            {completedSteps[2] ? "✓" : "2"}
          </span>
          <span className="step-name">Review Criteria</span>
        </div>

        <div
          className={`step ${step >= 3 ? "active" : ""} ${
            completedSteps[3] ? "completed" : ""
          } ${canAccessStep(3) ? "clickable" : "disabled"}`}
          onClick={() => handleStepClick(3)}
        >
          <span className="step-number">
            {completedSteps[3] ? "✓" : "3"}
          </span>
          <span className="step-name">Upload Bidders</span>
        </div>

        <div
          className={`step ${step >= 4 ? "active" : ""} ${
            completedSteps[4] ? "completed" : ""
          } ${canAccessStep(4) ? "clickable" : "disabled"}`}
          onClick={() => handleStepClick(4)}
        >
          <span className="step-number">
            {completedSteps[4] ? "✓" : "4"}
          </span>
          <span className="step-name">Evaluation</span>
        </div>
      </div>

      {/* Status Bar */}
      <div className="status-bar">
        {tenderData && (
          <span className="status-chip success">
            📄 Tender: {tenderData.title}
          </span>
        )}
        {tenderData && tenderData.criteria && (
          <span className="status-chip info">
            📋 {tenderData.criteria.length} Criteria
          </span>
        )}
        {bidders.length > 0 && (
          <span className="status-chip info">
            👥 {bidders.length} Bidder{bidders.length > 1 ? "s" : ""}
          </span>
        )}
        {evaluationResults && (
          <span className="status-chip success">
            ✅ Evaluation Complete
          </span>
        )}
      </div>

      <div className="card">
        {step === 1 && <TenderUpload onUploaded={handleTenderUploaded} existingTender={tenderData} />}

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

      {/* Navigation Buttons */}
      <div className="navigation">
        <button
          className="nav-btn"
          onClick={goBack}
          disabled={step === 1}
        >
          ⬅️ Back
        </button>
        <span className="step-indicator">Step {step} of 4</span>
        <button
          className="nav-btn"
          onClick={goNext}
          disabled={step === 4 || !canAccessStep(step + 1)}
        >
          Next ➡️
        </button>
      </div>
    </div>
  );
}

export default App;