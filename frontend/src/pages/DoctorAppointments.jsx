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

  if (loading) {
    return <p>Loading appointments...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  return (
    <div>
      <h2>My Appointments</h2>

      {appointments.length === 0 ? (
        <p>No appointments found.</p>
      ) : (
        appointments.map((appointment) => (
          <div key={appointment.id}>
            <p>
              <strong>Patient:</strong> {appointment.patient_name}
            </p>

            <p>
              <strong>Date:</strong> {appointment.appointment_date}
            </p>

            <p>
              <strong>Time:</strong> {appointment.appointment_time}
            </p>

            <hr />
          </div>
        ))
      )}
    </div>
  );
}

export default DoctorAppointments;