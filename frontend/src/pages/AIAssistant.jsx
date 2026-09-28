
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const normalize = (value = "") =>
  String(value).toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();

const specialtyGroups = [
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
    /\b(doctors?|physicians?|specialists?|cardiologists?|dermatologists?|neurologists?|pediatricians?|orthopedics?|orthopaedics?|gynecologists?|gynaecologists?|endocrinologists?|gastroenterologists?|psychiatrists?)\b/i.test(question);

  const hasDoctorName = /\bdr\.?\s+[a-z]/i.test(question);

  return hasLookupWord && (hasDoctorWord || hasDoctorName);
};

const findMatchingDoctors = (question, doctors) => {
  const query = normalize(question);
  const words = new Set(query.split(" "));

  // Match an actual doctor name first.
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

  // Match the requested specialty against database records.
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

  // General doctor search.
  return doctors;
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
    "What should I do if I have a fever?",
    "What are common symptoms of asthma?",
    "What is dengue?"
  ];

  // Redirect to booking page with the selected doctor.
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
      // Fetch actual doctor records for doctor lookups.
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

      // Healthcare questions and appointment requests.
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

            <div className="response-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
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