import { useState } from "react";
import {
  Link,
  useNavigate
} from "react-router-dom";

function Register() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/auth/register",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            name: name,
            email: email,
            password: password,
            age: Number(age),
            gender: gender
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Registration failed"
        );
      }

      setSuccess(
        "Registration successful! Redirecting to login..."
      );

      setTimeout(() => {
        navigate("/login");
      }, 1500);

    } catch (error) {

      setError(error.message);

    } finally {

      setLoading(false);

    }
  };

  return (
    <main className="auth-page">

      {/* =========================================
          ODASHA LOGO
          ========================================= */}

      <Link
        to="/"
        className="auth-logo"
      >
        ODASHA
      </Link>


      {/* =========================================
          REGISTER CARD
          ========================================= */}

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
          Create Account
        </h2>

        <p className="auth-subtitle">
          Register as a new patient
        </p>


        {/* =========================================
            REGISTRATION FORM
            ========================================= */}

        <form onSubmit={handleRegister}>

          {/* Name */}

          <div className="auth-form-group">

            <label>
              Full Name
            </label>

            <input
              type="text"
              value={name}
              onChange={(e) =>
                setName(e.target.value)
              }
              placeholder="Enter your full name"
              required
            />

          </div>


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
              placeholder="Create a password"
              required
            />

          </div>


          {/* Age */}

          <div className="auth-form-group">

            <label>
              Age
            </label>

            <input
              type="number"
              value={age}
              onChange={(e) =>
                setAge(e.target.value)
              }
              placeholder="Enter your age"
              min="1"
              required
            />

          </div>


          {/* Gender */}

          <div className="auth-form-group">

            <label>
              Gender
            </label>

            <select
              value={gender}
              onChange={(e) =>
                setGender(e.target.value)
              }
              required
            >

              <option value="">
                Select gender
              </option>

              <option value="Male">
                Male
              </option>

              <option value="Female">
                Female
              </option>

              <option value="Other">
                Other
              </option>

            </select>

          </div>


          {/* Error */}

          {error && (

            <div className="auth-error">
              {error}
            </div>

          )}


          {/* Success */}

          {success && (

            <div className="auth-success">
              {success}
            </div>

          )}


          {/* Register button */}

          <button
            type="submit"
            className="auth-submit-button"
            disabled={loading}
          >

            {loading
              ? "Creating Account..."
              : "Create Account"}

          </button>

        </form>


        {/* =========================================
            LOGIN LINK
            ========================================= */}

        <div className="auth-footer">

          <p>
            Already have an account?
          </p>

          <Link to="/login">
            Login
          </Link>

        </div>


        {/* =========================================
            BACK TO HOME
            ========================================= */}

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

export default Register;