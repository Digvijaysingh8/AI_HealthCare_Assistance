
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const normalize = (value = "") =>
  String(value).toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();

const specialtyGroups = [
  { query: ["dentist", "dentistry"], db: ["dentist", "dentistry"] },
  { query: ["cardiologist", "cardiology"], db: ["cardiology"] },
  { query: ["dermatologist", "dermatology"], db: ["dermatology"] },
  { query: ["neurologist", "neurology"], db: ["neurology"] },
  { query: ["pediatrician", "pediatrics"], db: ["pediatrics", "paediatrics"] },
  { query: ["orthopedic", "orthopaedic", "orthopedics"], db: ["orthopedic", "orthopaedic"] },
  { query: ["gynecologist", "gynaecologist", "gynecology", "gynaecology"], db: ["gynecology", "gynaecology"] },
  { query: ["general physician", "general medicine"], db: ["general medicine", "general physician"] },
  { query: ["endocrinologist", "endocrinology"], db: ["endocrinology"] },
  { query: ["gastroenterologist", "gastroenterology"], db: ["gastroenterology"] },
  { query: ["psychiatrist", "psychiatry"], db: ["psychiatry"] },
];

const isDoctorLookup = (question) => {
  const hasLookupWord =
    /\b(find|search|show|list|looking for|look for|which|who|available|have)\b/i.test(question);

  const hasDoctorWord =
    /\b(doctors?|physicians?|specialists?|dentists?|cardiologists?|dermatologists?|neurologists?|pediatricians?|orthopedics?|orthopaedics?|gynecologists?|gynaecologists?|endocrinologists?|gastroenterologists?|psychiatrists?)\b/i.test(question);

  const hasDoctorName = /\bdr\.?\s+[a-z]/i.test(question);

  return hasLookupWord && (hasDoctorWord || hasDoctorName);
};

const findMatchingDoctors = (question, doctors) => {
  const query = normalize(question);
  const words = new Set(query.split(" "));

  const namedDoctors = doctors.filter((doctor) => {
    const name = normalize(doctor.name).replace(/^dr\s+/, "");
    const parts = name.split(" ").filter((part) => part.length > 2);

    return (
      (name && query.includes(name)) ||
      parts.some((part) => words.has(part))
    );
  });

  if (namedDoctors.length > 0) {
    return namedDoctors;
  }

  const group = specialtyGroups.find((item) =>
    item.query.some((term) => query.includes(normalize(term)))
  );

  if (group) {
    return doctors.filter((doctor) => {
      const specialization = normalize(doctor.specialization);

      return group.db.some((term) =>
        specialization.includes(normalize(term))
      );
    });
  }

  return doctors;
};

// Styled Markdown components for AI responses.
const markdownComponents = {
  h1: ({ children }) => (
    <h1 style={{
      fontSize: "24px",
      fontWeight: 750,
      color: "#172554",
      margin: "8px 0 16px",
      lineHeight: 1.4
    }}>
      {children}
    </h1>
  ),

  h2: ({ children }) => (
    <h2 style={{
      fontSize: "21px",
      fontWeight: 700,
      color: "#1e3a8a",
      margin: "22px 0 10px",
      lineHeight: 1.4,
      borderBottom: "1px solid #e2e8f0",
      paddingBottom: "7px"
    }}>
      {children}
    </h2>
  ),

  h3: ({ children }) => (
    <h3 style={{
      fontSize: "17px",
      fontWeight: 700,
      color: "#334155",
      margin: "18px 0 8px"
    }}>
      {children}
    </h3>
  ),

  p: ({ children }) => (
    <p style={{
      color: "#334155",
      fontSize: "15px",
      lineHeight: 1.8,
      margin: "0 0 13px"
    }}>
      {children}
    </p>
  ),

  ul: ({ children }) => (
    <ul style={{
      margin: "8px 0 18px",
      paddingLeft: "24px",
      display: "grid",
      gap: "8px",
      listStyleType: "disc"
    }}>
      {children}
    </ul>
  ),

  ol: ({ children }) => (
    <ol style={{
      margin: "8px 0 18px",
      paddingLeft: "24px",
      display: "grid",
      gap: "8px",
      listStyleType: "decimal"
    }}>
      {children}
    </ol>
  ),

  li: ({ children }) => (
    <li style={{
      color: "#334155",
      fontSize: "15px",
      lineHeight: 1.7,
      paddingLeft: "3px"
    }}>
      {children}
    </li>
  ),

  strong: ({ children }) => (
    <strong style={{
      color: "#1e3a8a",
      fontWeight: 700
    }}>
      {children}
    </strong>
  ),

  blockquote: ({ children }) => (
    <blockquote style={{
      margin: "16px 0",
      padding: "12px 16px",
      background: "#eff6ff",
      borderLeft: "4px solid #3b82f6",
      borderRadius: "0 10px 10px 0",
      color: "#1e40af"
    }}>
      {children}
    </blockquote>
  ),

  table: ({ children }) => (
    <div style={{
      width: "100%",
      overflowX: "auto",
      margin: "16px 0",
      border: "1px solid #e2e8f0",
      borderRadius: "10px"
    }}>
      <table style={{
        width: "100%",
        borderCollapse: "collapse",
        fontSize: "14px",
        color: "#334155"
      }}>
        {children}
      </table>
    </div>
  ),

  thead: ({ children }) => (
    <thead style={{ background: "#eff6ff" }}>
      {children}
    </thead>
  ),

  th: ({ children }) => (
    <th style={{
      padding: "12px",
      textAlign: "left",
      color: "#1e3a8a",
      borderBottom: "1px solid #dbeafe"
    }}>
      {children}
    </th>
  ),

  td: ({ children }) => (
    <td style={{
      padding: "11px 12px",
      borderBottom: "1px solid #e2e8f0",
      lineHeight: 1.6
    }}>
      {children}
    </td>
  ),

  hr: () => (
    <hr style={{
      border: 0,
      borderTop: "1px solid #e2e8f0",
      margin: "20px 0"
    }} />
  ),

  code: ({ children, className }) => {
    const isBlock = Boolean(className);

    return (
      <code style={isBlock ? {
        display: "block",
        padding: "14px",
        background: "#0f172a",
        color: "#e2e8f0",
        borderRadius: "9px",
        overflowX: "auto",
        fontSize: "13px",
        lineHeight: 1.6
      } : {
        background: "#eff6ff",
        color: "#1d4ed8",
        borderRadius: "5px",
        padding: "2px 6px",
        fontSize: "0.9em"
      }}>
        {children}
      </code>
    );
  },

  pre: ({ children }) => (
    <pre style={{
      margin: "14px 0",
      whiteSpace: "pre-wrap",
      overflowX: "auto"
    }}>
      {children}
    </pre>
  ),

  a: ({ children, href }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      style={{
        color: "#2563eb",
        textDecoration: "underline",
        fontWeight: 600
      }}
    >
      {children}
    </a>
  )
};

function AIAssistant() {
  const navigate = useNavigate();

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [conversationHistory, setConversationHistory] = useState([]);
  const [showConfirmButton, setShowConfirmButton] = useState(false);
  const [appointmentThreadId, setAppointmentThreadId] = useState(null);
  const [doctorResults, setDoctorResults] = useState([]);
  const [showDoctorResults, setShowDoctorResults] = useState(false);

  const suggestions = [
    "What are the symptoms of diabetes?",
    "Find me a cardiologist",
    "What are common symptoms of asthma?",
    "What is dengue?"
  ];

  const bookDoctor = (doctor) => {
    navigate("/appointments", {
      state: {
        doctorId: Number(doctor.id),
        doctorName: doctor.name
      }
    });
  };

  const askQuestion = async (e) => {
    if (e) e.preventDefault();

    const questionToSend = question.trim();

    if (!questionToSend || loading) return;

    setLoading(true);
    setAnswer("");
    setError("");
    setShowConfirmButton(false);
    setAppointmentThreadId(null);
    setDoctorResults([]);
    setShowDoctorResults(false);

    const currentConversation = [
      ...conversationHistory,
      { role: "user", content: questionToSend }
    ];

    try {
      if (isDoctorLookup(questionToSend)) {
        const response = await fetch(
          "http://127.0.0.1:8000/doctors/",
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`
            }
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail || "Failed to fetch doctors"
          );
        }

        const matches = findMatchingDoctors(questionToSend, data);

        const responseText = matches.length
          ? "Here are the doctors matching your search in our database."
          : "No doctors matching your search were found in our database.";

        setDoctorResults(matches);
        setShowDoctorResults(true);
        setAnswer(responseText);

        setConversationHistory([
          ...currentConversation,
          { role: "assistant", content: responseText }
        ]);

        return;
      }

      const response = await fetch(
        "http://127.0.0.1:8000/ai/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`
          },
          body: JSON.stringify({
            question: questionToSend
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

      setConversationHistory([
        ...currentConversation,
        { role: "assistant", content: data.answer }
      ]);

      if (data.requires_confirmation && data.thread_id) {
        setShowConfirmButton(true);
        setAppointmentThreadId(data.thread_id);
      } else {
        setShowConfirmButton(false);
        setAppointmentThreadId(null);
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!appointmentThreadId || loading) return;

    setLoading(true);
    setError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/ai/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token")}`
          },
          body: JSON.stringify({
            question: "Confirm appointment",
            thread_id: appointmentThreadId,
            confirmed: true
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to confirm appointment"
        );
      }

      setAnswer(data.answer);

      setConversationHistory((previous) => [
        ...previous,
        { role: "user", content: "Confirmed appointment" },
        { role: "assistant", content: data.answer }
      ]);

      setShowConfirmButton(false);
      setAppointmentThreadId(null);
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
    setShowConfirmButton(false);
    setAppointmentThreadId(null);
    setDoctorResults([]);
    setShowDoctorResults(false);
  };

  const clearChat = () => {
    setConversationHistory([]);
    setQuestion("");
    setAnswer("");
    setError("");
    setShowConfirmButton(false);
    setAppointmentThreadId(null);
    setDoctorResults([]);
    setShowDoctorResults(false);
  };

  return (
    <main className="ai-page">
      {/* Hero */}
      <section className="ai-hero">
        <div className="ai-badge">
          ✦ AI HEALTHCARE ASSISTANT
        </div>

        <h2>How can we help you today?</h2>

        <p>
          Ask a healthcare-related question and get
          information based on our healthcare knowledge base.
        </p>
      </section>

      {/* Main AI Card */}
      <section className="ai-card">
        {/* Suggestions */}
        <div className="suggestions-section">
          <h3>Try asking</h3>

          <div className="suggestion-grid">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                className="suggestion-card"
                onClick={() => selectSuggestion(suggestion)}
              >
                <span className="suggestion-icon">+</span>
                <span>{suggestion}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Question Form */}
        <form className="ai-form" onSubmit={askQuestion}>
          <label>Your question</label>

          <div className="question-box">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Type your healthcare question here..."
              rows="4"
            />

            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="ask-button"
            >
              {loading ? "Thinking..." : "Ask AI"}
            </button>
          </div>
        </form>

        {/* Error */}
        {error && (
          <div className="ai-error">{error}</div>
        )}

        {/* AI Answer */}
        {answer && (
          <div className="ai-response">
            <div className="response-header">
              <div className="ai-avatar">AI</div>

              <div>
                <h3>Odasha AI</h3>
                <span>Healthcare Assistant</span>
              </div>
            </div>

            {/* Decorated Markdown response */}
            <div
              className="response-content"
              style={{
                background: "#ffffff",
                border: "1px solid #dbeafe",
                borderRadius: "16px",
                padding: "24px 28px",
                marginTop: "20px",
                color: "#334155",
                lineHeight: 1.8,
                overflowX: "auto",
                boxShadow: "0 4px 16px rgba(15, 23, 42, 0.04)"
              }}
            >
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={markdownComponents}
              >
                {answer}
              </ReactMarkdown>
            </div>

            {/* Doctor appointment cards */}
            {showDoctorResults && doctorResults.length > 0 && (
              <div className="ai-doctor-results">
                {doctorResults.map((doctor) => (
                  <div
                    className="ai-doctor-result"
                    key={doctor.id}
                  >
                    <div className="ai-doctor-info">
                      <strong>{doctor.name}</strong>
                      <span>
                        {doctor.specialization} · ID #{doctor.id}
                      </span>
                    </div>

                    <button
                      type="button"
                      className="ai-doctor-book-button"
                      onClick={() => bookDoctor(doctor)}
                    >
                      Book Appointment
                      <span aria-hidden="true"> →</span>
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* AI Action Buttons */}
            <div className="ai-action-buttons">
              {showConfirmButton && (
                <button
                  type="button"
                  className="confirm-ai-button"
                  onClick={handleConfirm}
                  disabled={loading}
                >
                  {loading ? "Booking..." : "Confirm"}
                </button>
              )}

              <button
                type="button"
                className="clear-ai-button"
                onClick={clearChat}
                disabled={loading}
              >
                Clear conversation
              </button>
            </div>
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