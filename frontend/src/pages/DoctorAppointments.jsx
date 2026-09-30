
import { useEffect, useState } from "react";

function DoctorAppointments() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchAppointments = async () => {
      const token = localStorage.getItem("access_token");

      try {
        const response = await fetch(
          "http://127.0.0.1:8000/appointments/my-doctor",
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail || "Failed to fetch appointments"
          );
        }

        setAppointments(data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAppointments();
  }, []);

  const today = new Date().toISOString().split("T")[0];

  const todayAppointments = appointments.filter(
    (appointment) => appointment.appointment_date === today
  ).length;

  const upcomingAppointments = appointments.filter(
    (appointment) => appointment.appointment_date >= today
  ).length;

  const formatDate = (date) => {
    if (!date) return "Date unavailable";

    const parsedDate = new Date(`${date}T00:00:00`);

    if (Number.isNaN(parsedDate.getTime())) {
      return date;
    }

    return parsedDate.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric"
    });
  };

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
    appointmentGrid: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
      gap: "20px"
    },
    appointmentCard: {
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
      width: "48px",
      height: "48px",
      borderRadius: "50%",
      background: "#dbeafe",
      color: "#2563eb",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontSize: "21px",
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
      margin: 0
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
            <p>Loading your appointments...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.page}>
        <div style={styles.container}>
          <div style={{
            ...styles.message,
            color: "#b91c1c",
            border: "1px solid #fecaca"
          }}>
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
            My Appointments
          </h2>
          <p style={styles.subtitle}>
            View and manage your patient appointments.
          </p>
        </div>

        {/* SUMMARY CARDS */}
        <div style={styles.summaryGrid}>
          <div style={styles.summaryCard}>
            <p style={styles.summaryLabel}>
              Total Appointments
            </p>
            <p style={{ ...styles.summaryValue, color: "#2563eb" }}>
              {appointments.length}
            </p>
          </div>

          <div style={styles.summaryCard}>
            <p style={styles.summaryLabel}>
              Today's Appointments
            </p>
            <p style={{ ...styles.summaryValue, color: "#059669" }}>
              {todayAppointments}
            </p>
          </div>

          <div style={styles.summaryCard}>
            <p style={styles.summaryLabel}>
              Upcoming Appointments
            </p>
            <p style={{ ...styles.summaryValue, color: "#7c3aed" }}>
              {upcomingAppointments}
            </p>
          </div>
        </div>

        {/* APPOINTMENT LIST */}
        <h3 style={styles.sectionTitle}>
          Appointment List
        </h3>

        {appointments.length === 0 ? (
          <div style={styles.empty}>
            <div style={{ fontSize: "48px", marginBottom: "12px" }}>
              📅
            </div>
            <h3 style={{ color: "#334155", margin: "0 0 8px" }}>
              No appointments yet
            </h3>
            <p style={{ margin: 0, fontSize: "14px" }}>
              Your scheduled patient appointments will appear here.
            </p>
          </div>
        ) : (
          <div style={styles.appointmentGrid}>
            {appointments.map((appointment) => (
              <div
                key={appointment.id}
                style={styles.appointmentCard}
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
                {/* PATIENT */}
                <div style={styles.patientRow}>
                  <div style={styles.avatar}>
                    {(appointment.patient_name || "P")
                      .trim()
                      .charAt(0)
                      .toUpperCase()}
                  </div>

                  <div style={{ minWidth: 0 }}>
                    <h3 style={styles.patientName}>
                      {appointment.patient_name || "Unknown Patient"}
                    </h3>
                    <p style={styles.patientLabel}>
                      Patient
                    </p>
                  </div>
                </div>

                {/* DATE */}
                <div style={styles.detail}>
                  <div style={styles.detailIcon}>📅</div>
                  <div>
                    <p style={styles.detailLabel}>
                      Appointment Date
                    </p>
                    <p style={styles.detailValue}>
                      {formatDate(appointment.appointment_date)}
                    </p>
                  </div>
                </div>

                {/* TIME */}
                <div style={styles.detail}>
                  <div style={styles.detailIcon}>🕒</div>
                  <div>
                    <p style={styles.detailLabel}>
                      Appointment Time
                    </p>
                    <p style={styles.detailValue}>
                      {appointment.appointment_time || "Time unavailable"}
                    </p>
                  </div>
                </div>

                {/* APPOINTMENT ID */}
                <div style={{
                  marginTop: "16px",
                  paddingTop: "12px",
                  borderTop: "1px solid #e2e8f0",
                  fontSize: "12px",
                  color: "#94a3b8"
                }}>
                  Appointment ID: #{appointment.id}
                </div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}

export default DoctorAppointments;