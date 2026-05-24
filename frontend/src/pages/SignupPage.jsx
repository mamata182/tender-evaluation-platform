import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { signupApi } from "../services/api";

function SignupPage() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    password: "",
    confirm_password: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });

    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (
      !formData.full_name ||
      !formData.email ||
      !formData.password ||
      !formData.confirm_password
    ) {
      setError("Please fill all fields");
      return;
    }

    if (formData.password !== formData.confirm_password) {
      setError("Passwords do not match");
      return;
    }

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await signupApi(
        formData.full_name,
        formData.email,
        formData.password,
        formData.confirm_password
      );

      navigate("/login", {
        replace: true,
        state: {
          message: "Account created successfully. Please login.",
          email: formData.email,
        },
      });
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Signup failed. Try another email or login if already registered."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-modern-page signup-variant">
      <div className="auth-modern-left signup-left">
        <div className="auth-modern-overlay"></div>

        <div className="auth-modern-brand">
          <div className="brand-badge">Create Your Evaluation Workspace</div>

          <h1>
            Start Smarter
            <span> Procurement</span>
          </h1>

          <p>
            Create an account to access the AI-based tender eligibility platform
            for automated criteria extraction, bidder evaluation and explainable
            decision support.
          </p>

          <div className="signup-process-card">
            <h3>Platform Workflow</h3>

            <div className="process-step">
              <span>01</span>
              <p>Upload tender document</p>
            </div>

            <div className="process-step">
              <span>02</span>
              <p>AI extracts eligibility criteria</p>
            </div>

            <div className="process-step">
              <span>03</span>
              <p>Upload bidder submissions</p>
            </div>

            <div className="process-step">
              <span>04</span>
              <p>Generate explainable evaluation</p>
            </div>
          </div>
        </div>
      </div>

      <div className="auth-modern-right">
        <div className="auth-modern-form-card signup-card">
          <div className="auth-mini-logo">🚀</div>

          <h2>Create Account</h2>
          <p className="auth-modern-subtitle">
            Register first. After signup, you will be redirected to login.
          </p>

          {error && <div className="auth-modern-error">{error}</div>}

          <form onSubmit={handleSubmit} className="auth-modern-form">
            <div className="modern-input-group">
              <label>Full Name</label>
              <input
                type="text"
                name="full_name"
                placeholder="Enter your full name"
                value={formData.full_name}
                onChange={handleChange}
              />
            </div>

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
                placeholder="Minimum 6 characters"
                value={formData.password}
                onChange={handleChange}
              />
            </div>

            <div className="modern-input-group">
              <label>Confirm Password</label>
              <input
                type="password"
                name="confirm_password"
                placeholder="Confirm your password"
                value={formData.confirm_password}
                onChange={handleChange}
              />
            </div>

            <button
              className="modern-auth-btn"
              type="submit"
              disabled={loading}
            >
              {loading ? "Creating account..." : "Create Account"}
            </button>
          </form>

          <div className="modern-auth-links">
            <p>
              Already registered? <Link to="/login">Login</Link>
            </p>
            <Link to="/">← Back to Home</Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SignupPage;