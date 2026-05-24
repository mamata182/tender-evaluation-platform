import { useNavigate } from "react-router-dom";

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="land-page">
      {/* NAVBAR */}
      <nav className="land-nav">
        <div className="land-logo">
          <div className="land-logo-icon">🏛️</div>
          <div>
            <h2>TenderAI</h2>
            <span>Government Procurement Intelligence</span>
          </div>
        </div>

        <div className="land-nav-links">
          <button className="land-nav-link" onClick={() => navigate("/login")}>
            Login
          </button>
          <button
            className="land-nav-btn"
            onClick={() => navigate("/signup")}
          >
            Get Started Free
          </button>
        </div>
      </nav>

      {/* HERO */}
      <section className="land-hero">
        <div className="land-hero-bg"></div>
        <div className="land-hero-particles">
          <div className="particle p1"></div>
          <div className="particle p2"></div>
          <div className="particle p3"></div>
          <div className="particle p4"></div>
          <div className="particle p5"></div>
        </div>

        <div className="land-hero-content">
          <div className="land-hero-badge">
            <span className="badge-dot"></span>
            AI-Powered Tender Evaluation Platform
          </div>

          <h1 className="land-hero-title">
            Automate Government
            <br />
            <span>Tender Evaluation</span>
            <br />
            with AI Intelligence
          </h1>

          <p className="land-hero-desc">
            Extract eligibility criteria from complex tender documents, process
            bidder submissions in any format, and generate explainable eligibility
            decisions — all powered by AI and OCR.
          </p>

          <div className="land-hero-actions">
            <button
              className="land-primary-btn"
              onClick={() => navigate("/signup")}
            >
              🚀 Start Free Evaluation
            </button>
            <button
              className="land-outline-btn"
              onClick={() => navigate("/login")}
            >
              Login to Dashboard →
            </button>
          </div>

          <div className="land-hero-stats">
            <div className="hero-stat">
              <h3>100%</h3>
              <p>Automated</p>
            </div>
            <div className="hero-stat-divider"></div>
            <div className="hero-stat">
              <h3>AI</h3>
              <p>Powered</p>
            </div>
            <div className="hero-stat-divider"></div>
            <div className="hero-stat">
              <h3>OCR</h3>
              <p>Supported</p>
            </div>
            <div className="hero-stat-divider"></div>
            <div className="hero-stat">
              <h3>3</h3>
              <p>Decision Types</p>
            </div>
          </div>
        </div>

        <div className="land-hero-visual">
          <div className="hero-visual-card main-card">
            <div className="visual-card-header">
              <span></span>
              <span></span>
              <span></span>
              <strong>Evaluation Results</strong>
            </div>

            <div className="visual-bidder eligible-bidder">
              <div>
                <strong>TATA Motors Ltd</strong>
                <small>13/13 criteria met</small>
              </div>
              <span>✅ Eligible</span>
            </div>

            <div className="visual-bidder danger-bidder">
              <div>
                <strong>New Electric Motors</strong>
                <small>6/13 criteria met</small>
              </div>
              <span>❌ Not Eligible</span>
            </div>

            <div className="visual-bidder warning-bidder">
              <div>
                <strong>Ashok Leyland Ltd</strong>
                <small>11/13 criteria met</small>
              </div>
              <span>⚠️ Review</span>
            </div>

            <div className="visual-confidence">
              <div>
                <small>AI Confidence</small>
                <strong>92%</strong>
              </div>
              <div className="conf-bar">
                <div className="conf-fill"></div>
              </div>
            </div>
          </div>

          <div className="hero-visual-card mini-card criteria-card">
            <div className="mini-card-title">Extracted Criteria</div>
            <div className="criteria-tag financial">💰 Financial</div>
            <div className="criteria-tag technical">🔧 Technical</div>
            <div className="criteria-tag compliance">📜 Compliance</div>
          </div>

          <div className="hero-visual-card mini-card ocr-card">
            <div className="mini-card-title">Document Types</div>
            <div className="doc-item">📄 Typed PDF</div>
            <div className="doc-item">🖨️ Scanned PDF</div>
            <div className="doc-item">📝 Word / DOCX</div>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="land-steps-section">
        <div className="land-section-label">Simple Process</div>
        <h2>How TenderAI Works</h2>
        <p>
          From tender upload to final eligibility decision in four steps.
        </p>

        <div className="land-steps-grid">
          <div className="land-step-card">
            <div className="step-num">01</div>
            <div className="step-icon">📤</div>
            <h3>Upload Tender</h3>
            <p>
              Upload any government tender document in PDF, DOCX or image
              format. Works with scanned and low-quality documents via OCR.
            </p>
          </div>

          <div className="land-step-connector">→</div>

          <div className="land-step-card">
            <div className="step-num">02</div>
            <div className="step-icon">🤖</div>
            <h3>AI Extraction</h3>
            <p>
              AI reads tender text and extracts eligibility criteria classified
              into Technical, Financial and Compliance categories.
            </p>
          </div>

          <div className="land-step-connector">→</div>

          <div className="land-step-card">
            <div className="step-num">03</div>
            <div className="step-icon">👥</div>
            <h3>Upload Bidders</h3>
            <p>
              Upload multiple bidder submissions in any format. AI extracts
              relevant data like turnover, certifications, and project history.
            </p>
          </div>

          <div className="land-step-connector">→</div>

          <div className="land-step-card">
            <div className="step-num">04</div>
            <div className="step-icon">📊</div>
            <h3>Get Decision</h3>
            <p>
              Each bidder receives Eligible, Not Eligible or Needs Review
              status with criterion-level reasoning and evidence.
            </p>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="land-features-section">
        <div className="land-features-left">
          <div className="land-section-label">Platform Capabilities</div>
          <h2>Built for Government Procurement</h2>
          <p>
            Designed to match real-world procurement workflows with strict
            requirements for transparency, consistency, and auditability.
          </p>

          <div className="land-feature-list">
            <div className="land-feature-item">
              <div className="feature-check">✓</div>
              <div>
                <h4>OCR Support</h4>
                <p>Process scanned PDFs, images and low-quality documents.</p>
              </div>
            </div>

            <div className="land-feature-item">
              <div className="feature-check">✓</div>
              <div>
                <h4>AI Extraction</h4>
                <p>
                  LLM extracts eligibility criteria from complex legal tender language.
                </p>
              </div>
            </div>

            <div className="land-feature-item">
              <div className="feature-check">✓</div>
              <div>
                <h4>Explainable Decisions</h4>
                <p>
                  Every decision shows evidence, source text and confidence score.
                </p>
              </div>
            </div>

            <div className="land-feature-item">
              <div className="feature-check">✓</div>
              <div>
                <h4>Human Review Safety</h4>
                <p>
                  Ambiguous cases are flagged, not rejected automatically.
                </p>
              </div>
            </div>

            <div className="land-feature-item">
              <div className="feature-check">✓</div>
              <div>
                <h4>Report Download</h4>
                <p>
                  Download consolidated evaluation report after each run.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="land-features-right">
          <div className="features-preview-window">
            <div className="window-header">
              <span className="win-dot red"></span>
              <span className="win-dot yellow"></span>
              <span className="win-dot green"></span>
              <strong>AI Criteria Extraction</strong>
            </div>

            <div className="window-body">
              <div className="extracted-criterion financial-c">
                <span>💰</span>
                <div>
                  <strong>Minimum Annual Turnover</strong>
                  <small>≥ 50 crore | Financial | Mandatory</small>
                </div>
                <span className="conf-badge">90%</span>
              </div>

              <div className="extracted-criterion technical-c">
                <span>🔧</span>
                <div>
                  <strong>Electric Buses Supplied</strong>
                  <small>≥ 50 buses | Technical | Mandatory</small>
                </div>
                <span className="conf-badge">85%</span>
              </div>

              <div className="extracted-criterion compliance-c">
                <span>📜</span>
                <div>
                  <strong>ISO 9001:2015 Certificate</strong>
                  <small>Must have | Compliance | Mandatory</small>
                </div>
                <span className="conf-badge">95%</span>
              </div>

              <div className="extracted-criterion compliance-c">
                <span>📜</span>
                <div>
                  <strong>Valid GST Registration</strong>
                  <small>Must have | Compliance | Mandatory</small>
                </div>
                <span className="conf-badge">98%</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* DECISION SECTION */}
      <section className="land-decision-section">
        <div className="land-section-label light">Evaluation Engine</div>
        <h2>Three-Way Eligibility Decision</h2>
        <p>
          Every bidder is evaluated fairly with evidence-backed decisions.
        </p>

        <div className="land-decision-grid">
          <div className="land-decision-card eligible-card">
            <div className="decision-icon">✅</div>
            <h3>Eligible</h3>
            <p>
              Bidder satisfies all mandatory criteria with sufficient evidence
              and confidence above threshold.
            </p>
            <div className="decision-example">
              Example: TATA Motors — 13/13 criteria met
            </div>
          </div>

          <div className="land-decision-card not-eligible-card">
            <div className="decision-icon">❌</div>
            <h3>Not Eligible</h3>
            <p>
              Bidder clearly fails one or more mandatory criteria with high
              confidence rejection reasoning.
            </p>
            <div className="decision-example">
              Example: New Electric — 6/13 criteria met
            </div>
          </div>

          <div className="land-decision-card review-card">
            <div className="decision-icon">⚠️</div>
            <h3>Needs Review</h3>
            <p>
              Ambiguous or incomplete data detected. Flagged for manual review
              instead of automatic rejection.
            </p>
            <div className="decision-example">
              Example: Ashok Leyland — uncertain data found
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="land-cta-section">
        <div className="land-cta-content">
          <h2>Start Evaluating Tenders with AI Today</h2>
          <p>
            Create your free account and upload your first tender document in
            minutes.
          </p>

          <div className="land-cta-buttons">
            <button
              className="land-primary-btn"
              onClick={() => navigate("/signup")}
            >
              🚀 Create Free Account
            </button>
            <button
              className="land-outline-btn-light"
              onClick={() => navigate("/login")}
            >
              Login →
            </button>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="land-footer">
        <div className="land-footer-inner">
          <div className="land-footer-brand">
            <h3>🏛️ TenderAI</h3>
            <p>AI-Based Tender Evaluation Platform</p>
            <p>Government of Karnataka Procurement Systems</p>
          </div>

          <div className="land-footer-links">
            <strong>Platform</strong>
            <span onClick={() => navigate("/signup")}>Get Started</span>
            <span onClick={() => navigate("/login")}>Login</span>
            <span onClick={() => navigate("/signup")}>Create Account</span>
          </div>

          <div className="land-footer-links">
            <strong>Technology</strong>
            <span>FastAPI Backend</span>
            <span>React Frontend</span>
            <span>Groq AI</span>
            <span>Tesseract OCR</span>
          </div>

          <div className="land-footer-links">
            <strong>Deployment</strong>
            <span>Hosted on Render</span>
            <span>Live 24/7</span>
            <span>Auto Deploy</span>
          </div>
        </div>

        <div className="land-footer-bottom">
          <p>© 2025 KaroStartup Technology India Pvt Ltd. All rights reserved.</p>
          <p>Built for Government of Karnataka Procurement Systems.</p>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;