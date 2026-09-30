
import { useEffect, useState } from "react";
import { API_URL } from "../api"; 
function MyPatients() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPatients = async () => {
      const token = localStorage.getItem("access_token");

      try {
        const response = await fetch(
          `${API_URL}/doctors/my-patients`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail || "Failed to fetch patients"
          );
        }

        setPatients(data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPatients();
  }, []);

  const malePatients = patients.filter(
    (patient) =>
      (patient.gender || "").toLowerCase() === "male"
  ).length;

  const femalePatients = patients.filter(
    (patient) =>
      (patient.gender || "").toLowerCase() === "female"
  ).length;

  const styles = {
    page: {
      minHeight: "calc(100vh - 160px)",
      background: "#f4f7fb",
      padding: "35px 5%",
      fontFamily: "Arial, sans-serif",
      color: "#1e293b"
    },
    container: {
      maxWidth: "1200px",
      margin: "0 auto"
    },
    heading: {
      fontSize: "30px",
      fontWeight: "700",
      margin: "0 0 8px",
      color: "#172554"
    },
    subtitle: {
      fontSize: "15px",
      color: "#64748b",
      margin: "0 0 28px"
    },
    summaryGrid: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))",
      gap: "18px",
      marginBottom: "32px"
    },
    summaryCard: {
      background: "#ffffff",
      borderRadius: "16px",
      padding: "22px",
      boxShadow: "0 4px 16px rgba(15, 23, 42, 0.06)",
      border: "1px solid #e5eaf2"
    },
    summaryLabel: {
      color: "#64748b",
      fontSize: "14px",
      margin: "0 0 12px"
    },
    summaryValue: {
      fontSize: "30px",
      fontWeight: "700",
      margin: 0
    },
    sectionTitle: {
      fontSize: "21px",
      fontWeight: "700",
      margin: "0 0 18px",
      color: "#172554"
    },
    patientGrid: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
      gap: "20px"
    },
    patientCard: {
      background: "#ffffff",
      borderRadius: "16px",
      padding: "22px",
      boxShadow: "0 4px 16px rgba(15, 23, 42, 0.06)",
      border: "1px solid #e5eaf2",
      transition: "transform 0.2s ease, box-shadow 0.2s ease"
    },
    patientRow: {
      display: "flex",
      alignItems: "center",
      gap: "13px",
      marginBottom: "20px"
    },
    avatar: {
      width: "52px",
      height: "52px",
      borderRadius: "50%",
      background: "#dbeafe",
      color: "#2563eb",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontSize: "22px",
      fontWeight: "700",
      flexShrink: 0
    },
    patientName: {
      fontSize: "17px",
      fontWeight: "700",
      color: "#1e293b",
      margin: "0 0 4px",
      overflowWrap: "anywhere"
    },
    patientLabel: {
      fontSize: "12px",
      color: "#64748b",
      margin: 0
    },
    detail: {
      display: "flex",
      alignItems: "center",
      gap: "10px",
      padding: "11px 12px",
      background: "#f8fafc",
      borderRadius: "10px",
      marginBottom: "10px"
    },
    detailIcon: {
      width: "34px",
      height: "34px",
      borderRadius: "9px",
      background: "#e0e7ff",
      color: "#4f46e5",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontSize: "17px",
      flexShrink: 0
    },
    detailLabel: {
      fontSize: "11px",
      color: "#64748b",
      margin: "0 0 3px"
    },
    detailValue: {
      fontSize: "14px",
      fontWeight: "600",
      color: "#334155",
      margin: 0,
      textTransform: "capitalize"
    },
    empty: {
      background: "#ffffff",
      border: "1px dashed #cbd5e1",
      borderRadius: "16px",
      padding: "50px 20px",
      textAlign: "center",
      color: "#64748b"
    },
    message: {
      background: "#ffffff",
      borderRadius: "14px",
      padding: "24px",
      textAlign: "center",
      color: "#475569"
    }
  };

  if (loading) {
    return (
      <div style={styles.page}>
        <div style={styles.container}>
          <div style={styles.message}>
            <div style={{ fontSize: "30px", marginBottom: "10px" }}>
              ⏳
            </div>
            <p>Loading your patients...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.page}>
        <div style={styles.container}>
          <div
            style={{
              ...styles.message,
              color: "#b91c1c",
              border: "1px solid #fecaca"
            }}
          >
            <div style={{ fontSize: "28px" }}>⚠️</div>
            <p>{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.page}>
      <div style={styles.container}>

        {/* PAGE HEADER */}
        <div style={{ marginBottom: "28px" }}>
          <h2 style={styles.heading}>
            My Patients
          </h2>
          <p style={styles.subtitle}>
            View the patients assigned to your care.
          </p>
        </div>

        {/* SUMMARY CARDS */}
        <div style={styles.summaryGrid}>
          <div style={styles.summaryCard}>
            <p style={styles.summaryLabel}>
              Total Patients
            </p>
            <p style={{ ...styles.summaryValue, color: "#2563eb" }}>
              {patients.length}
            </p>
          </div>

          <div style={styles.summaryCard}>
            <p style={styles.summaryLabel}>
              Male Patients
            </p>
            <p style={{ ...styles.summaryValue, color: "#059669" }}>
              {malePatients}
            </p>
          </div>

          <div style={styles.summaryCard}>
            <p style={styles.summaryLabel}>
              Female Patients
            </p>
            <p style={{ ...styles.summaryValue, color: "#9333ea" }}>
              {femalePatients}
            </p>
          </div>
        </div>

        {/* PATIENT LIST */}
        <h3 style={styles.sectionTitle}>
          Patient List
        </h3>

        {patients.length === 0 ? (
          <div style={styles.empty}>
            <div style={{ fontSize: "48px", marginBottom: "12px" }}>
              👥
            </div>
            <h3 style={{ color: "#334155", margin: "0 0 8px" }}>
              No patients yet
            </h3>
            <p style={{ margin: 0, fontSize: "14px" }}>
              Your patients will appear here when they have appointments with you.
            </p>
          </div>
        ) : (
          <div style={styles.patientGrid}>
            {patients.map((patient) => (
              <div
                key={patient.id}
                style={styles.patientCard}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-4px)";
                  e.currentTarget.style.boxShadow =
                    "0 10px 24px rgba(15, 23, 42, 0.10)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow =
                    "0 4px 16px rgba(15, 23, 42, 0.06)";
                }}
              >
                {/* PATIENT HEADER */}
                <div style={styles.patientRow}>
                  <div style={styles.avatar}>
                    {(patient.name || "P")
                      .trim()
                      .charAt(0)
                      .toUpperCase()}
                  </div>

                  <div style={{ minWidth: 0 }}>
                    <h3 style={styles.patientName}>
                      {patient.name || "Unknown Patient"}
                    </h3>
                    <p style={styles.patientLabel}>
                      Patient ID: #{patient.id}
                    </p>
                  </div>
                </div>

                {/* AGE */}
                <div style={styles.detail}>
                  <div style={styles.detailIcon}>🎂</div>
                  <div>
                    <p style={styles.detailLabel}>
                      Age
                    </p>
                    <p style={styles.detailValue}>
                      {patient.age != null
                        ? `${patient.age} years`
                        : "Not available"}
                    </p>
                  </div>
                </div>

                {/* GENDER */}
                <div style={styles.detail}>
                  <div style={styles.detailIcon}>👤</div>
                  <div>
                    <p style={styles.detailLabel}>
                      Gender
                    </p>
                    <p style={styles.detailValue}>
                      {patient.gender || "Not available"}
                    </p>
                  </div>
                </div>

              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}

export default MyPatients;