
import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import DatePicker from "react-datepicker";

import "react-datepicker/dist/react-datepicker.css";

function Appointments() {
  const location = useLocation();

  useEffect(() => {
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: "instant",
    });
  }, []);

  const selectedDoctorFromCard =
    location.state?.doctorId || "";

  const selectedDoctorNameFromCard =
    location.state?.doctorName || "";

  const userRole = localStorage.getItem("user_role");

  const [availableSlots, setAvailableSlots] = useState([]);
  const [loadingSlots, setLoadingSlots] = useState(false);

  const [doctors, setDoctors] = useState([]);

  const [doctorId, setDoctorId] = useState(
    selectedDoctorFromCard
  );

  const [patientId, setPatientId] = useState("");
  const [currentPatient, setCurrentPatient] = useState(null);

  const [appointmentDate, setAppointmentDate] = useState("");
  const [appointmentTime, setAppointmentTime] = useState("");

  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);

  // Fetch logged-in user, patient and doctors.
  const fetchData = async () => {
    setLoading(true);

    try {
      const token = localStorage.getItem("access_token");

      const userResponse = await fetch(
        "http://127.0.0.1:8000/auth/me",
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!userResponse.ok) {
        throw new Error("Failed to fetch logged-in user");
      }

      const userData = await userResponse.json();

      if (userData.role === "patient") {
        const patientsResponse = await fetch(
          "http://127.0.0.1:8000/patients/",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!patientsResponse.ok) {
          throw new Error("Failed to fetch patients");
        }

        const patientsData = await patientsResponse.json();

        const loggedInPatient = patientsData.find(
          (patient) => patient.user_id === userData.id
        );

        if (!loggedInPatient) {
          throw new Error("Patient profile not found");
        }

        setCurrentPatient(loggedInPatient);
        setPatientId(String(loggedInPatient.id));
      }

      const doctorsResponse = await fetch(
        "http://127.0.0.1:8000/doctors/"
      );

      if (!doctorsResponse.ok) {
        throw new Error("Failed to fetch doctors");
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
      alert(error.message);
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
          `http://127.0.0.1:8000/appointments/available-slots/${doctorId}?appointment_date=${appointmentDate}`
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

    if (userRole === "patient" && currentPatient) {
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

    if (userRole === "patient" && !currentPatient) {
      alert("Patient profile not found.");
      return;
    }

    setBooking(true);

    try {
      const token = localStorage.getItem("access_token");

      const selectedPatientId =
        userRole === "patient"
          ? currentPatient.id
          : patientId;

      if (!selectedPatientId) {
        alert("Please select a patient.");
        return;
      }

      const appointmentResponse = await fetch(
        "http://127.0.0.1:8000/appointments/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            patient_id: Number(selectedPatientId),
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
      alert(error.message);
    } finally {
      setBooking(false);
    }
  };

  const selectedDoctor = doctors.find(
    (doctor) => String(doctor.id) === String(doctorId)
  );

  return (
    <main className="page">
      {userRole === "patient" && (
        <>
          <h2>Book an Appointment</h2>

          <p>
            Schedule a consultation with one of our available doctors.
          </p>

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

            {/* Date */}
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

            {/* Time */}
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
                !currentPatient
              }
            >
              {booking ? "Booking..." : "Book Appointment"}
            </button>
          </form>
        </>
      )}
    </main>
  );
}

export default Appointments;