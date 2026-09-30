
import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import DatePicker from "react-datepicker";

import "react-datepicker/dist/react-datepicker.css";

const API_URL = "http://127.0.0.1:8000";

function Appointments() {
  const location = useLocation();

  useEffect(() => {
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: "instant",
    });
  }, []);

  const selectedDoctorFromCard = location.state?.doctorId || "";
  const selectedDoctorNameFromCard =
    location.state?.doctorName || "";

  const userRole = localStorage.getItem("user_role");

  const [availableSlots, setAvailableSlots] = useState([]);
  const [loadingSlots, setLoadingSlots] = useState(false);

  const [doctors, setDoctors] = useState([]);
  const [doctorId, setDoctorId] = useState(
    String(selectedDoctorFromCard)
  );

  const [patientId, setPatientId] = useState("");
  const [currentPatient, setCurrentPatient] = useState(null);

  const [appointmentDate, setAppointmentDate] = useState("");
  const [appointmentTime, setAppointmentTime] = useState("");

  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);
  const [error, setError] = useState("");

  // Fetch the logged-in patient and available doctors.
  const fetchData = async () => {
    setLoading(true);
    setError("");

    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        throw new Error("Please log in to book an appointment.");
      }

      const userResponse = await fetch(`${API_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!userResponse.ok) {
        const data = await userResponse.json().catch(() => ({}));
        throw new Error(
          data.detail ||
            `Failed to fetch logged-in user (${userResponse.status})`
        );
      }

      const userData = await userResponse.json();

      if (userData.role !== "patient") {
        throw new Error("Only patients can book appointments.");
      }

      // Fetch only the authenticated patient's profile.
      const patientResponse = await fetch(
        `${API_URL}/patients/me`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!patientResponse.ok) {
        const data = await patientResponse.json().catch(() => ({}));
        throw new Error(
          data.detail ||
            `Failed to fetch patient profile (${patientResponse.status})`
        );
      }

      const loggedInPatient = await patientResponse.json();

      if (!loggedInPatient?.id) {
        throw new Error("Patient profile not found.");
      }

      setCurrentPatient(loggedInPatient);
      setPatientId(String(loggedInPatient.id));

      // Fetch doctors.
      const doctorsResponse = await fetch(`${API_URL}/doctors/`);

      if (!doctorsResponse.ok) {
        const data = await doctorsResponse.json().catch(() => ({}));
        throw new Error(
          data.detail ||
            `Failed to fetch doctors (${doctorsResponse.status})`
        );
      }

      const doctorsData = await doctorsResponse.json();
      setDoctors(doctorsData);

      // Preserve the doctor selected on the Doctors page.
      if (selectedDoctorFromCard) {
        const doctorExists = doctorsData.some(
          (doctor) =>
            String(doctor.id) === String(selectedDoctorFromCard)
        );

        if (doctorExists) {
          setDoctorId(String(selectedDoctorFromCard));
        }
      }
    } catch (error) {
      console.error("Error fetching appointment data:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Fetch available slots whenever doctor or date changes.
  useEffect(() => {
    const fetchAvailableSlots = async () => {
      if (!doctorId || !appointmentDate) {
        setAvailableSlots([]);
        setAppointmentTime("");
        return;
      }

      setLoadingSlots(true);

      try {
        const response = await fetch(
          `${API_URL}/appointments/available-slots/${doctorId}?appointment_date=${appointmentDate}`
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail || "Failed to fetch available slots"
          );
        }

        setAvailableSlots(data);
        setAppointmentTime("");
      } catch (error) {
        console.error("Error fetching available slots:", error);
        setAvailableSlots([]);
      } finally {
        setLoadingSlots(false);
      }
    };

    fetchAvailableSlots();
  }, [doctorId, appointmentDate]);

  // Reset the form after booking.
  const resetForm = () => {
    if (selectedDoctorFromCard) {
      setDoctorId(String(selectedDoctorFromCard));
    } else {
      setDoctorId("");
    }

    setAppointmentDate("");
    setAppointmentTime("");

    if (currentPatient) {
      setPatientId(String(currentPatient.id));
    } else {
      setPatientId("");
    }

    setAvailableSlots([]);
  };

  // Book an appointment.
  const bookAppointment = async (e) => {
    e.preventDefault();

    if (!doctorId || !appointmentDate || !appointmentTime) {
      alert("Please fill all appointment details.");
      return;
    }

    if (!currentPatient) {
      alert("Patient profile not found. Please refresh the page.");
      return;
    }

    setBooking(true);

    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        throw new Error("Please log in again.");
      }

      const appointmentResponse = await fetch(
        `${API_URL}/appointments/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            patient_id: Number(currentPatient.id),
            doctor_id: Number(doctorId),
            appointment_date: appointmentDate,
            appointment_time: appointmentTime,
          }),
        }
      );

      const appointmentData = await appointmentResponse.json();

      if (!appointmentResponse.ok) {
        throw new Error(
          appointmentData.detail || "Failed to book appointment"
        );
      }

      alert("Appointment booked successfully!");
      resetForm();
    } catch (error) {
      console.error("Error booking appointment:", error);
      alert(error.message);
    } finally {
      setBooking(false);
    }
  };

  const selectedDoctor = doctors.find(
    (doctor) => String(doctor.id) === String(doctorId)
  );

  if (userRole !== "patient") {
    return (
      <main className="page">
        <p>Only patients can book appointments.</p>
      </main>
    );
  }

  return (
    <main className="page">
      <h2>Book an Appointment</h2>

      <p>
        Schedule a consultation with one of our available doctors.
      </p>

      {error && (
        <div
          role="alert"
          style={{
            color: "#b91c1c",
            backgroundColor: "#fee2e2",
            padding: "12px",
            borderRadius: "8px",
            marginBottom: "16px",
          }}
        >
          <strong>Error:</strong> {error}
          <button
            type="button"
            onClick={fetchData}
            disabled={loading}
            style={{ marginLeft: "12px" }}
          >
            {loading ? "Loading..." : "Retry"}
          </button>
        </div>
      )}

      <form
        className="appointment-form"
        onSubmit={bookAppointment}
      >
        {/* Patient Information */}
        <div className="appointment-section-title">
          <h3>Patient Information</h3>
        </div>

        <div className="form-group">
          <label>Patient</label>

          <input
            type="text"
            value={
              currentPatient
                ? currentPatient.name
                : loading
                ? "Loading patient..."
                : "Patient unavailable"
            }
            readOnly
          />
        </div>

        {/* Appointment Details */}
        <div className="appointment-section-title">
          <h3>Appointment Details</h3>
        </div>

        {/* Doctor */}
        <div className="form-group">
          <label>Doctor</label>

          {selectedDoctorFromCard ? (
            <input
              type="text"
              value={
                selectedDoctor?.name ||
                selectedDoctorNameFromCard ||
                "Loading doctor..."
              }
              readOnly
            />
          ) : (
            <select
              value={doctorId}
              onChange={(e) => setDoctorId(e.target.value)}
              disabled={loading}
            >
              <option value="">Select Doctor</option>

              {doctors.map((doctor) => (
                <option key={doctor.id} value={doctor.id}>
                  {doctor.name}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Appointment Date */}
        <div className="form-group">
          <label>Appointment Date</label>

          <DatePicker
            selected={
              appointmentDate
                ? new Date(`${appointmentDate}T00:00:00`)
                : null
            }
            onChange={(selectedDate) => {
              if (!selectedDate) {
                setAppointmentDate("");
                setAppointmentTime("");
                return;
              }

              const year = selectedDate.getFullYear();
              const month = String(
                selectedDate.getMonth() + 1
              ).padStart(2, "0");
              const day = String(
                selectedDate.getDate()
              ).padStart(2, "0");

              setAppointmentDate(`${year}-${month}-${day}`);
            }}
            minDate={new Date()}
            dateFormat="dd-MM-yyyy"
            placeholderText="Select appointment date"
            className="appointment-date-picker"
          />
        </div>

        {/* Appointment Time */}
        <div className="form-group">
          <label>Appointment Time</label>

          {!doctorId || !appointmentDate ? (
            <p>Please select a doctor and date first.</p>
          ) : loadingSlots ? (
            <p>Loading available slots...</p>
          ) : availableSlots.length === 0 ? (
            <p>No available slots for this date.</p>
          ) : (
            <div className="time-slots">
              {availableSlots.map((slot) => (
                <button
                  type="button"
                  key={slot.time}
                  disabled={!slot.available}
                  className={
                    !slot.available
                      ? "time-slot booked"
                      : appointmentTime === slot.time
                      ? "time-slot selected"
                      : "time-slot"
                  }
                  onClick={() => {
                    if (slot.available) {
                      setAppointmentTime(slot.time);
                    }
                  }}
                >
                  {slot.time}

                  {!slot.available && (
                    <span className="booked-mark">✕</span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Book Button */}
        <button
          type="submit"
          disabled={
            booking ||
            loading ||
            loadingSlots ||
            !currentPatient ||
            !doctorId ||
            !appointmentDate ||
            !appointmentTime
          }
        >
          {booking ? "Booking..." : "Book Appointment"}
        </button>
      </form>
    </main>
  );
}

export default Appointments;