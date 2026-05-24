import { useState } from "react";
import { useNavigate, Link, useLocation } from "react-router-dom";
import { loginApi } from "../services/api";
import { saveToken, saveUser } from "../services/auth";

function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const [formData, setFormData] = useState({
    email: location.state?.email || "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const successMessage = location.state?.message || "";

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });

    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.email || !formData.password) {
      setError("Please enter email and password");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await loginApi(formData.email, formData.password);

      saveToken(data.access_token);
      saveUser(data.user);

      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.response?.data?.detail || "Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-modern-page">
      <div className="auth-modern-left">
        <div className="auth-modern-overlay"></div>

        <div className="auth-modern-brand">
          <div className="brand-badge">Government Procurement AI</div>

          <h1>
            Tender Evaluation
            <span> Intelligence</span>
          </h1>

          <p>
            Securely access your AI-powered tender evaluation workspace to
            process tender documents, bidder submissions and eligibility
            decisions.
          </p>

          <div className="auth-preview-card">
            <div className="preview-header">
              <span></span>
              <span></span>
              <span></span>
            </div>

            <div className="preview-title">Live Evaluation Preview</div>

            <div className="preview-row success">
              <div>
                <strong>Eligible</strong>
                <small>TATA Motors</small>
              </div>
              <span>13/13</span>
            </div>

            <div className="preview-row danger">
              <div>
                <strong>Not Eligible</strong>
                <small>Motor Ltd</small>
              </div>
              <span>6/13</span>
            </div>

            <div className="preview-row warning">
              <div>
                <strong>Needs Review</strong>
                <small>Ashok Leyland</small>
              </div>
              <span>11/13</span>
            </div>
          </div>
        </div>
      </div>

      <div className="auth-modern-right">
        <div className="auth-modern-form-card">
          <div className="auth-mini-logo">🏛️</div>

          <h2>Welcome Back</h2>
          <p className="auth-modern-subtitle">
            Login to continue to your evaluation dashboard
          </p>

          {successMessage && (
            <div className="auth-modern-success">{successMessage}</div>
          )}

          {error && <div className="auth-modern-error">{error}</div>}

          <form onSubmit={handleSubmit} className="auth-modern-form">
            <div className="modern-input-group">
              <label>Email Address</label>
              <input
                type="email"
                name="email"
                placeholder="example@email.com"
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div className="modern-input-group">
              <label>Password</label>
              <input
                type="password"
                name="password"
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleChange}
              />
            </div>

            <button
              className="modern-auth-btn"
              type="submit"
              disabled={loading}
            >
              {loading ? "Logging in..." : "Login to Dashboard"}
            </button>
          </form>

          <div className="modern-auth-links">
            <p>
              New user? <Link to="/signup">Create Account</Link>
            </p>
            <Link to="/">← Back to Home</Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;