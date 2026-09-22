import { useState } from "react";

function AIAssistant() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const suggestions = [
    "What are the symptoms of diabetes?",
    "What should I do if I have a fever?",
    "What are common symptoms of asthma?",
    "What is dengue?"
  ];

  const askQuestion = async (e) => {
    e.preventDefault();

    if (!question.trim()) {
      return;
    }

    setLoading(true);
    setAnswer("");
    setError("");

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
        throw new Error(
          data.detail || "Failed to get AI response"
        );
      }

      setAnswer(data.answer);

    } catch (error) {
      setError(error.message);

    } finally {
      setLoading(false);
    }
  };

  const selectSuggestion = (suggestion) => {
    setQuestion(suggestion);
    setAnswer("");
    setError("");
  };

  const clearChat = () => {
    setQuestion("");
    setAnswer("");
    setError("");
  };

  return (
    <main className="ai-page">

      {/* Hero */}

      <section className="ai-hero">

        <div className="ai-badge">
          ✦ AI HEALTHCARE ASSISTANT
        </div>

        <h2>
          How can we help you today?
        </h2>

        <p>
          Ask a healthcare-related question and get
          information based on our healthcare knowledge base.
        </p>

      </section>


      {/* Main AI Card */}

      <section className="ai-card">

        {/* Suggestions */}

        <div className="suggestions-section">

          <h3>
            Try asking
          </h3>

          <div className="suggestion-grid">

            {suggestions.map((suggestion, index) => (

              <button
                key={index}
                className="suggestion-card"
                onClick={() =>
                  selectSuggestion(suggestion)
                }
              >
                <span className="suggestion-icon">
                  +
                </span>

                <span>
                  {suggestion}
                </span>

              </button>

            ))}

          </div>

        </div>


        {/* Question Form */}

        <form
          className="ai-form"
          onSubmit={askQuestion}
        >

          <label>
            Your question
          </label>

          <div className="question-box">

            <textarea
              value={question}
              onChange={(e) =>
                setQuestion(e.target.value)
              }
              placeholder="Type your healthcare question here..."
              rows="4"
            />

            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="ask-button"
            >
              {loading
                ? "Thinking..."
                : "Ask AI"}
            </button>

          </div>

        </form>


        {/* Error */}

        {error && (

          <div className="ai-error">
            {error}
          </div>

        )}


        {/* AI Answer */}

        {answer && (

          <div className="ai-response">

            <div className="response-header">

              <div className="ai-avatar">
                AI
              </div>

              <div>
                <h3>
                  Odasha AI
                </h3>

                <span>
                  Healthcare Assistant
                </span>
              </div>

            </div>

            <div className="response-content">
              {answer}
            </div>

            <button
              className="clear-ai-button"
              onClick={clearChat}
            >
              Clear conversation
            </button>

          </div>

        )}

      </section>


      {/* Disclaimer */}

      <p className="ai-disclaimer">
        This assistant provides general healthcare information
        and is not a substitute for professional medical advice.
      </p>

    </main>
  );
}

export default AIAssistant;