import { useState } from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

import Patients from "./pages/Patients";
import Doctors from "./pages/Doctors";
import Appointments from "./pages/Appointments";

import "./App.css";


function App() {

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);


  const clearChat = () => {
    setQuestion("");
    setAnswer("");
  };


  const askQuestion = async () => {

    if (!question.trim()) {
      return;
    }

    setLoading(true);
    setAnswer("");

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/ai/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            question: question
          })
        }
      );


      const data = await response.json();


      if (!response.ok) {
        throw new Error("API request failed");
      }


      setAnswer(data.answer);
      setQuestion("");


    } catch (error) {

      setAnswer(
        "Something went wrong. Please try again."
      );

    }


    setLoading(false);
  };


  return (
    <BrowserRouter>

      <div className="app">

        {/* Header */}

        <header className="header">

          <h1>AI Healthcare Assistant</h1>

          <p>
            Your personal healthcare information assistant
          </p>


          {/* Navigation */}

          <nav className="navbar">

            <Link to="/">
              <button>Home</button>
            </Link>

            <Link to="/patients">
              <button>Patients</button>
            </Link>

            <Link to="/doctors">
              <button>Doctors</button>
            </Link>

            <Link to="/appointments">
              <button>Appointments</button>
            </Link>

          </nav>

        </header>


        {/* Pages */}

        <Routes>


          {/* Home / AI Assistant */}

          <Route
            path="/"
            element={

              <main className="chat-container">


                {/* Welcome message */}

                <div className="welcome-message">

                  <h2>
                    How can I help you?
                  </h2>

                  <p>
                    Ask a healthcare-related question and I will
                    provide information based on the available
                    healthcare knowledge.
                  </p>

                </div>


                {/* Suggestions */}

                <div className="suggestions">

                  <p>
                    Try asking:
                  </p>


                  <div className="suggestion-buttons">

                    <button
                      onClick={() =>
                        setQuestion("What is diabetes?")
                      }
                    >
                      What is diabetes?
                    </button>


                    <button
                      onClick={() =>
                        setQuestion(
                          "What are common symptoms of asthma?"
                        )
                      }
                    >
                      Asthma symptoms
                    </button>


                    <button
                      onClick={() =>
                        setQuestion("What is dengue?")
                      }
                    >
                      What is dengue?
                    </button>

                  </div>

                </div>


                {/* Question input */}

                <div className="input-area">

                  <textarea
                    placeholder="Ask your healthcare question..."
                    rows="4"
                    value={question}
                    onChange={(e) =>
                      setQuestion(e.target.value)
                    }
                  />


                  {/* Ask button */}

                  <button
                    onClick={askQuestion}
                    disabled={loading}
                  >
                    {loading
                      ? "Thinking..."
                      : "Ask Question"}
                  </button>


                  {/* Answer */}

                  {answer && (

                    <div className="answer-area">

                      <h3>
                        Answer
                      </h3>

                      <p>
                        {answer}
                      </p>

                    </div>

                  )}


                  {/* Clear button */}

                  {answer && (

                    <div className="clear-container">

                      <button
                        className="clear-button"
                        onClick={clearChat}
                        disabled={loading}
                      >
                        Clear
                      </button>

                    </div>

                  )}

                </div>

              </main>

            }
          />


          {/* Patients */}

          <Route
            path="/patients"
            element={<Patients />}
          />


          {/* Doctors */}

          <Route
            path="/doctors"
            element={<Doctors />}
          />


          {/* Appointments */}

          <Route
            path="/appointments"
            element={<Appointments />}
          />


        </Routes>

      </div>

    </BrowserRouter>
  );
}


export default App;