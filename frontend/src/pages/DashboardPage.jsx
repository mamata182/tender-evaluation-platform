import { useNavigate } from "react-router-dom";
import { getUser, logout } from "../services/auth";

function DashboardPage() {
  const navigate = useNavigate();
  const user = getUser();

  const firstName = user?.full_name?.split(" ")[0] || "User";
  const avatarLetter = user?.full_name?.charAt(0)?.toUpperCase() || "U";

  const backendDocsUrl =
    import.meta.env.VITE_API_URL
      ? `${import.meta.env.VITE_API_URL}/docs`
      : "http://127.0.0.1:8000/docs";

  return (
    <div className="new-dashboard">
      <nav className="new-dashboard-nav">
        <div className="new-brand">
          <div className="new-brand-icon">🏛️</div>
          <div>
            <h2>TenderAI</h2>
            <p>Government Procurement Intelligence</p>
          </div>
        </div>

        <div className="new-user-area">
          <div className="new-user-card">
            <span>{avatarLetter}</span>
            <div>
              <strong>{user?.full_name || "User"}</strong>
              <small>{user?.email || "Procurement Officer"}</small>
            </div>
          </div>

          <button className="new-logout-btn" onClick={logout}>
            Logout
          </button>
        </div>
      </nav>

      <main className="new-dashboard-main">
        <section className="new-hero-card">
          <div className="new-hero-content">
            <div className="new-badge">AI-Powered Tender Intelligence</div>

            <h1>
              Welcome back, <span>{firstName}</span>
            </h1>

            <p>
              Upload tender documents, extract eligibility criteria, process
              bidder submissions, and generate explainable eligibility decisions
              using AI and OCR.
            </p>

            <div className="new-hero-buttons">
              <button
                className="new-primary-btn"
                onClick={() => navigate("/evaluate")}
              >
                🚀 Start New Evaluation
              </button>

              <button
                className="new-secondary-btn"
                onClick={() => window.open(backendDocsUrl, "_blank")}
              >
                📘 View API Docs
              </button>
            </div>
          </div>

          <div className="new-ai-panel">
            <div className="new-ai-circle">
              <span>AI</span>
            </div>
            <h3>Smart Tender Engine</h3>
            <p>OCR + LLM + Rule Engine + Explainability</p>
          </div>
        </section>

        <section className="new-stats">
          <div className="new-stat-card">
            <div className="new-stat-icon violet">📄</div>
            <h3>Multi Format</h3>
            <p>PDF, DOCX, scanned files and images</p>
          </div>

          <div className="new-stat-card">
            <div className="new-stat-icon blue">🤖</div>
            <h3>AI Extraction</h3>
            <p>LLM-based tender and bidder analysis</p>
          </div>

          <div className="new-stat-card">
            <div className="new-stat-icon green">✅</div>
            <h3>3-Way Decision</h3>
            <p>Eligible, Not Eligible and Needs Review</p>
          </div>

          <div className="new-stat-card">
            <div className="new-stat-icon orange">🔍</div>
            <h3>Explainable</h3>
            <p>Criterion-level reasoning and confidence</p>
          </div>
        </section>

        <section className="new-workflow-section">
          <div className="new-section-header">
            <div>
              <h2>Procurement Workflow</h2>
              <p>Follow the complete AI-powered evaluation process</p>
            </div>

            <button
              className="new-dark-btn"
              onClick={() => navigate("/evaluate")}
            >
              New Workflow →
            </button>
          </div>

          <div className="new-workflow-grid">
            <div
              className="new-workflow-card active"
              onClick={() => navigate("/evaluate")}
            >
              <span className="new-number">01</span>
              <div className="new-workflow-icon">📤</div>
              <h3>Upload Tender</h3>
              <p>
                Upload government tender documents and extract eligibility
                criteria automatically.
              </p>
              <strong>Start Evaluation →</strong>
            </div>

            <div className="new-workflow-card">
              <span className="new-number">02</span>
              <div className="new-workflow-icon">📋</div>
              <h3>Review Criteria</h3>
              <p>
                View categorized Technical, Financial and Compliance
                requirements.
              </p>
            </div>

            <div className="new-workflow-card">
              <span className="new-number">03</span>
              <div className="new-workflow-icon">👥</div>
              <h3>Upload Bidders</h3>
              <p>
                Process bidder documents using OCR and intelligent extraction.
              </p>
            </div>

            <div className="new-workflow-card">
              <span className="new-number">04</span>
              <div className="new-workflow-icon">📊</div>
              <h3>Generate Results</h3>
              <p>
                Get decisions with reasoning, confidence score, and evidence.
              </p>
            </div>
          </div>
        </section>

        <section className="new-capabilities">
          <div>
            <h2>System Capabilities</h2>
            <p>
              Designed for real-world government procurement workflows with
              transparency, reliability, and auditability.
            </p>
          </div>

          <div className="new-capability-grid">
            <div className="new-capability-item">
              <span>🧾</span>
              <div>
                <h4>Document Understanding</h4>
                <p>OCR-based extraction for scanned PDFs and images.</p>
              </div>
            </div>

            <div className="new-capability-item">
              <span>🧠</span>
              <div>
                <h4>AI-Assisted Evaluation</h4>
                <p>LLM and rule-based matching for tender eligibility.</p>
              </div>
            </div>

            <div className="new-capability-item">
              <span>🛡️</span>
              <div>
                <h4>Human Review Safety</h4>
                <p>Ambiguous cases are flagged instead of rejected.</p>
              </div>
            </div>

            <div className="new-capability-item">
              <span>📥</span>
              <div>
                <h4>Report Download</h4>
                <p>Download consolidated evaluation report after analysis.</p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default DashboardPage;