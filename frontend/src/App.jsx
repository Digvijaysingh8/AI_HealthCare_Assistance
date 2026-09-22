import { useEffect, useState } from "react";

import {
  BrowserRouter,
  Routes,
  Route,
  Link
} from "react-router-dom";

import MyAppointments from "./pages/MyAppointments";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Patients from "./pages/Patients";
import Doctors from "./pages/Doctors";
import Appointments from "./pages/Appointments";
import MyPatients from "./pages/MyPatients";
import DoctorAppointments from "./pages/DoctorAppointments";
import AIAssistant from "./pages/AIAssistant";

import ProtectedRoute from "./ProtectedRoute";

import "./App.css";


function App() {

  const [userRole, setUserRole] = useState(
    localStorage.getItem("user_role")
  );

  const [isLoggedIn, setIsLoggedIn] = useState(
    !!localStorage.getItem("access_token")
  );


  useEffect(() => {

    const checkLogin = () => {

      setIsLoggedIn(
        !!localStorage.getItem("access_token")
      );

      setUserRole(
        localStorage.getItem("user_role")
      );

    };

    window.addEventListener(
      "loginStatusChanged",
      checkLogin
    );

    return () => {

      window.removeEventListener(
        "loginStatusChanged",
        checkLogin
      );

    };

  }, []);


  const handleLogout = () => {

    localStorage.removeItem("access_token");
    localStorage.removeItem("user_role");
    localStorage.removeItem("user_email");

    setIsLoggedIn(false);
    setUserRole(null);

    window.location.href = "/";

  };


  return (

    <BrowserRouter>

      <div className="app">

        {/* =========================================
            NAVBAR
            ========================================= */}

        {isLoggedIn && (

          <header className="header">

            <h1>
              AI Healthcare Assistant
            </h1>

            <p>
              Your personal healthcare information assistant
            </p>


            <nav className="navbar">

              <Link to="/doctors">
                <button>
                  Doctors
                </button>
              </Link>


              {/* PATIENT */}

              {userRole === "patient" && (
                <>

                  <Link to="/my-appointments">
                    <button>
                      My Appointments
                    </button>
                  </Link>

                  <Link to="/appointments">
                    <button>
                      Book Appointment
                    </button>
                  </Link>

                  <Link to="/ai-assistant">
                    <button>
                      AI Assistant
                    </button>
                  </Link>

                </>
              )}


              {/* DOCTOR */}

              {userRole === "doctor" && (
                <>

                  <Link to="/my-patients">
                    <button>
                      My Patients
                    </button>
                  </Link>

                  <Link to="/doctor-appointments">
                    <button>
                      My Appointments
                    </button>
                  </Link>

                  <Link to="/ai-assistant">
                    <button>
                      AI Assistant
                    </button>
                  </Link>

                </>
              )}


              {/* ADMIN */}

              {userRole === "admin" && (
                <>

                  <Link to="/patients">
                    <button>
                      Patients
                    </button>
                  </Link>

                  <Link to="/doctors">
                    <button>
                      Doctors
                    </button>
                  </Link>

                  <Link to="/appointments">
                    <button>
                      Appointments
                    </button>
                  </Link>

                  <Link to="/ai-assistant">
                    <button>
                      AI Assistant
                    </button>
                  </Link>

                </>
              )}


              <button
                onClick={handleLogout}
              >
                Logout
              </button>

            </nav>

          </header>

        )}


        {/* =========================================
            ROUTES
            ========================================= */}

        <Routes>

          {/* PUBLIC HOME */}

          <Route
            path="/"
            element={

              <main className="landing-page">

                <div className="landing-card">

                  <h1>
                    Welcome to Odasha
                  </h1>

                  <p className="landing-subtitle">
                    Your personal AI-powered healthcare assistant
                  </p>

                  <p className="landing-description">
                    Get healthcare information, manage your
                    appointments, and connect with your
                    healthcare services in one place.
                  </p>

                  <div className="landing-buttons">

                    <Link to="/login">
                      <button className="landing-login-button">
                        Login
                      </button>
                    </Link>

                    <Link to="/register">
                      <button className="landing-register-button">
                        Register
                      </button>
                    </Link>

                  </div>

                  <p className="landing-register-text">
                    Your health. Your care. Your assistant.
                  </p>

                </div>

              </main>

            }
          />


          {/* LOGIN */}

          <Route
            path="/login"
            element={<Login />}
          />


          {/* REGISTER */}

          <Route
            path="/register"
            element={<Register />}
          />


          {/* DOCTORS */}

          <Route
            path="/doctors"
            element={

              <ProtectedRoute>

                <Doctors />

              </ProtectedRoute>

            }
          />


          {/* PATIENTS */}

          <Route
            path="/patients"
            element={

              <ProtectedRoute>

                <Patients />

              </ProtectedRoute>

            }
          />


          {/* BOOK APPOINTMENT */}

          <Route
            path="/appointments"
            element={

              <ProtectedRoute>

                <Appointments />

              </ProtectedRoute>

            }
          />


          {/* MY APPOINTMENTS */}

          <Route
            path="/my-appointments"
            element={

              <ProtectedRoute>

                <MyAppointments />

              </ProtectedRoute>

            }
          />


          {/* MY PATIENTS */}

          <Route
            path="/my-patients"
            element={

              <ProtectedRoute>

                <MyPatients />

              </ProtectedRoute>

            }
          />


          {/* DOCTOR APPOINTMENTS */}

          <Route
            path="/doctor-appointments"
            element={

              <ProtectedRoute>

                <DoctorAppointments />

              </ProtectedRoute>

            }
          />


          {/* AI ASSISTANT */}

          <Route
            path="/ai-assistant"
            element={

              <ProtectedRoute>

                <AIAssistant />

              </ProtectedRoute>

            }
          />

        </Routes>

      </div>

    </BrowserRouter>

  );

}

export default App;