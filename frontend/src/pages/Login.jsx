import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/auth/login",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            email: email,
            password: password
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Login failed"
        );
      }

      localStorage.setItem(
        "access_token",
        data.access_token
      );

      localStorage.setItem(
        "user_role",
        data.role
      );

      localStorage.setItem(
        "user_email",
        data.email
      );

      /*
        Notify the application that login happened.
      */

      window.dispatchEvent(
        new Event("loginStatusChanged")
      );

      /*
        Reload the application so the navbar
        immediately updates.
      */

      window.location.href = "/ai-assistant";

    } catch (error) {

      setError(error.message);

    } finally {

      setLoading(false);

    }
  };


  return (
    <main className="auth-page">
        <Link to="/" className="auth-logo">
            ODASHA
            </Link>

      <div className="auth-card">

        {/* Brand */}

        <div className="auth-brand">
          <span>
            ODASHA
          </span>

          <p>
            SMART HEALTHCARE
          </p>
        </div>


        {/* Heading */}

        <h2>
          Welcome Back
        </h2>

        <p className="auth-subtitle">
          Login to your healthcare account
        </p>


        {/* Form */}

        <form onSubmit={handleLogin}>

          {/* Email */}

          <div className="auth-form-group">

            <label>
              Email Address
            </label>

            <input
              type="email"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              placeholder="Enter your email"
              required
            />

          </div>


          {/* Password */}

          <div className="auth-form-group">

            <label>
              Password
            </label>

            <input
              type="password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              placeholder="Enter your password"
              required
            />

          </div>


          {/* Error */}

          {error && (

            <div className="auth-error">
              {error}
            </div>

          )}


          {/* Login */}

          <button
            type="submit"
            className="auth-submit-button"
            disabled={loading}
          >

            {loading
              ? "Logging in..."
              : "Login"}

          </button>

        </form>


        {/* Register */}

        <div className="auth-footer">

          <p>
            New patient?
          </p>

          <Link to="/register">
            Create an account
          </Link>

        </div>


        {/* Back */}

        <Link
          to="/"
          className="auth-back-link"
        >
          ← Back to Home
        </Link>

      </div>

    </main>
  );
}

export default Login;