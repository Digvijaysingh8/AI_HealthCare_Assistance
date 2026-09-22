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
    behavior: "instant"
  });
}, []);

  /*
    Doctor selected from the Doctors page.

    Example:
    Doctors page
       ↓
    Dr. Vijay
       ↓
    Book Appointment
       ↓
    doctorId is passed here
  */

  const selectedDoctorFromCard =
    location.state?.doctorId || "";

  const selectedDoctorNameFromCard =
    location.state?.doctorName || "";

  const userRole = localStorage.getItem("user_role");

  const [availableSlots, setAvailableSlots] = useState([]);
  const [loadingSlots, setLoadingSlots] = useState(false);

  const [patients, setPatients] = useState([]);
  const [doctors, setDoctors] = useState([]);

  /*
    If we came from a doctor card,
    automatically select that doctor.
  */

  const [doctorId, setDoctorId] = useState(
    selectedDoctorFromCard
  );

  const [appointments, setAppointments] = useState([]);

  const [patientId, setPatientId] = useState("");
  const [currentPatient, setCurrentPatient] = useState(null);

  const [appointmentDate, setAppointmentDate] = useState("");
  const [appointmentTime, setAppointmentTime] = useState("");

  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);


  /*
    ============================================================
    FETCH PATIENTS, DOCTORS AND APPOINTMENTS
    ============================================================
  */

  const fetchData = async () => {
    setLoading(true);

    try {
      const token =
        localStorage.getItem("access_token");

      /*
        1. Get logged-in user
      */

      const userResponse = await fetch(
        "http://127.0.0.1:8000/auth/me",
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      if (!userResponse.ok) {
        throw new Error(
          "Failed to fetch logged-in user"
        );
      }

      const userData =
        await userResponse.json();


      /*
        2. Get patients
      */

      const patientsResponse = await fetch(
        "http://127.0.0.1:8000/patients/"
      );

      if (!patientsResponse.ok) {
        throw new Error(
          "Failed to fetch patients"
        );
      }

      const patientsData =
        await patientsResponse.json();

      setPatients(patientsData);


      /*
        3. Find logged-in patient
      */

      if (userData.role === "patient") {

        const loggedInPatient =
          patientsData.find(
            (patient) =>
              patient.user_id === userData.id
          );

        if (!loggedInPatient) {
          throw new Error(
            "Patient profile not found"
          );
        }

        setCurrentPatient(
          loggedInPatient
        );

        setPatientId(
          loggedInPatient.id
        );
      }


      /*
        4. Get doctors
      */

      const doctorsResponse = await fetch(
        "http://127.0.0.1:8000/doctors/"
      );

      if (!doctorsResponse.ok) {
        throw new Error(
          "Failed to fetch doctors"
        );
      }

      const doctorsData =
        await doctorsResponse.json();

      setDoctors(doctorsData);


      /*
        IMPORTANT:
        If doctor was selected from
        Doctors page, keep that doctor selected.
      */

      if (selectedDoctorFromCard) {

        const doctorExists =
          doctorsData.some(
            (doctor) =>
              String(doctor.id) ===
              String(selectedDoctorFromCard)
          );

        if (doctorExists) {
          setDoctorId(
            String(selectedDoctorFromCard)
          );
        }
      }


      /*
        5. Get appointments

        Patient:
        /appointments/my

        Admin:
        /appointments/
      */

      const appointmentsUrl =
        userData.role === "patient"
          ? "http://127.0.0.1:8000/appointments/my"
          : "http://127.0.0.1:8000/appointments/";

      const appointmentsResponse =
        await fetch(
          appointmentsUrl,
          {
            headers: {
              Authorization:
                `Bearer ${token}`
            }
          }
        );

      if (!appointmentsResponse.ok) {
        throw new Error(
          "Failed to fetch appointments"
        );
      }

      const appointmentsData =
        await appointmentsResponse.json();

      setAppointments(
        appointmentsData
      );

    } catch (error) {

      console.error(
        "Error fetching appointment data:",
        error
      );

      alert(error.message);

    } finally {

      setLoading(false);

    }
  };


  useEffect(() => {
    fetchData();
  }, []);


  /*
    ============================================================
    FETCH AVAILABLE SLOTS
    ============================================================
  */

  useEffect(() => {

    fetchAvailableSlots();

  }, [doctorId, appointmentDate]);


  const fetchAvailableSlots = async () => {

    if (!doctorId || !appointmentDate) {

      setAvailableSlots([]);

      return;
    }

    setLoadingSlots(true);

    try {

      const response = await fetch(
        `http://127.0.0.1:8000/appointments/available-slots/${doctorId}?appointment_date=${appointmentDate}`
      );

      const data =
        await response.json();

      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Failed to fetch available slots"
        );

      }

      setAvailableSlots(data);

      setAppointmentTime("");

    } catch (error) {

      console.error(
        "Error fetching available slots:",
        error
      );

      setAvailableSlots([]);

    } finally {

      setLoadingSlots(false);

    }
  };


  /*
    ============================================================
    RESET APPOINTMENT FORM
    ============================================================
  */

  const resetForm = () => {

    /*
      If the patient came from a doctor card,
      keep that doctor selected.

      Otherwise clear doctor selection.
    */

    if (selectedDoctorFromCard) {

      setDoctorId(
        String(selectedDoctorFromCard)
      );

    } else {

      setDoctorId("");

    }

    setAppointmentDate("");
    setAppointmentTime("");


    /*
      Keep logged-in patient's own ID.
    */

    if (
      userRole === "patient" &&
      currentPatient
    ) {

      setPatientId(
        currentPatient.id
      );

    } else {

      setPatientId("");

    }
  };


  /*
    ============================================================
    BOOK APPOINTMENT
    ============================================================
  */

  const bookAppointment = async (e) => {

    e.preventDefault();

    if (
      !doctorId ||
      !appointmentDate ||
      !appointmentTime
    ) {

      alert(
        "Please fill all appointment details."
      );

      return;
    }


    /*
      Patient must have own profile.
    */

    if (
      userRole === "patient" &&
      !currentPatient
    ) {

      alert(
        "Patient profile not found."
      );

      return;
    }


    setBooking(true);

    try {

      const token =
        localStorage.getItem(
          "access_token"
        );


      /*
        Patients ALWAYS use their
        own patient ID.
      */

      const selectedPatientId =
        userRole === "patient"
          ? currentPatient.id
          : patientId;


      if (!selectedPatientId) {

        alert(
          "Please select a patient."
        );

        return;
      }


      const appointmentResponse =
        await fetch(
          "http://127.0.0.1:8000/appointments/",
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",

              Authorization:
                `Bearer ${token}`
            },

            body: JSON.stringify({
              patient_id:
                Number(selectedPatientId),

              doctor_id:
                Number(doctorId),

              appointment_date:
                appointmentDate,

              appointment_time:
                appointmentTime
            })
          }
        );


      const appointmentData =
        await appointmentResponse.json();


      if (!appointmentResponse.ok) {

        throw new Error(
          appointmentData.detail ||
          "Failed to book appointment"
        );

      }


      alert(
        "Appointment booked successfully!"
      );


      resetForm();

      await fetchData();

    } catch (error) {

      alert(error.message);

    } finally {

      setBooking(false);

    }
  };


  /*
    ============================================================
    GET SELECTED DOCTOR
    ============================================================
  */

  const selectedDoctor =
    doctors.find(
      (doctor) =>
        String(doctor.id) ===
        String(doctorId)
    );


  return (

    <main className="page">

      {/* =====================================================
          PATIENT BOOKING
          ===================================================== */}

      {userRole === "patient" && (

        <>

          <h2>
            Book an Appointment
          </h2>

          <p>
            Schedule a consultation with
            one of our available doctors.
          </p>


          <form
            className="appointment-form"
            onSubmit={bookAppointment}
          >

            {/* =================================================
                PATIENT INFORMATION
                ================================================= */}

            <div className="appointment-section-title">

              <h3>
                Patient Information
              </h3>

            </div>


            <div className="form-group">

              <label>
                Patient
              </label>

              <input
                type="text"

                value={
                  currentPatient
                    ? currentPatient.name
                    : "Loading patient..."
                }

                readOnly
              />

            </div>


            {/* =================================================
                APPOINTMENT DETAILS
                ================================================= */}

            <div className="appointment-section-title">

              <h3>
                Appointment Details
              </h3>

            </div>


            {/* =================================================
                DOCTOR
                ================================================= */}

            <div className="form-group">

              <label>
                Doctor
              </label>


              {selectedDoctorFromCard ? (

                /*
                  Doctor came from Doctors page.

                  Show it as a read-only field
                  instead of allowing the patient
                  to accidentally choose another doctor.
                */

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

                /*
                  Normal booking from navbar.
                  Patient can choose any doctor.
                */

                <select
                  value={doctorId}
                  onChange={(e) =>
                    setDoctorId(
                      e.target.value
                    )
                  }
                >

                  <option value="">
                    Select Doctor
                  </option>

                  {doctors.map(
                    (doctor) => (

                      <option
                        key={doctor.id}
                        value={doctor.id}
                      >
                        {doctor.name}
                      </option>

                    )
                  )}

                </select>

              )}

            </div>


            {/* =================================================
                DATE
                ================================================= */}

            <div className="form-group">

              <label>
                Appointment Date
              </label>

              <DatePicker

                selected={
                  appointmentDate
                    ? new Date(
                        appointmentDate +
                        "T00:00:00"
                      )
                    : null
                }

                onChange={(date) => {

                  if (!date) {

                    setAppointmentDate("");

                    return;
                  }


                  const year =
                    date.getFullYear();

                  const month =
                    String(
                      date.getMonth() + 1
                    ).padStart(2, "0");

                  const day =
                    String(
                      date.getDate()
                    ).padStart(2, "0");


                  setAppointmentDate(
                    `${year}-${month}-${day}`
                  );

                }}

                minDate={new Date()}

                dateFormat="dd-MM-yyyy"

                placeholderText=
                  "Select appointment date"

                className=
                  "appointment-date-picker"
              />

            </div>


            {/* =================================================
                TIME
                ================================================= */}

            <div className="form-group">

              <label>
                Appointment Time
              </label>


              {!doctorId ||
              !appointmentDate ? (

                <p>
                  Please select a doctor
                  and date first.
                </p>

              ) : loadingSlots ? (

                <p>
                  Loading available slots...
                </p>

              ) : availableSlots.length === 0 ? (

                <p>
                  No available slots
                  for this date.
                </p>

              ) : (

                <div className="time-slots">

                  {availableSlots.map(
                    (slot) => (

                      <button
                        type="button"
                        key={slot.time}
                        disabled={
                          !slot.available
                        }

                        className={
                          !slot.available
                            ? "time-slot booked"
                            : appointmentTime ===
                              slot.time
                            ? "time-slot selected"
                            : "time-slot"
                        }

                        onClick={() => {

                          if (
                            slot.available
                          ) {

                            setAppointmentTime(
                              slot.time
                            );

                          }

                        }}
                      >

                        {slot.time}

                        {!slot.available && (

                          <span
                            className="booked-mark"
                          >
                            ✕
                          </span>

                        )}

                      </button>

                    )
                  )}

                </div>

              )}

            </div>


            {/* =================================================
                BOOK BUTTON
                ================================================= */}

            <button
              type="submit"
              disabled={
                booking ||
                loading
              }
            >

              {booking
                ? "Booking..."
                : "Book Appointment"}

            </button>

          </form>

        </>

      )}


      {/* =====================================================
          APPOINTMENTS
          ===================================================== */}

<div className="appointment-section">

  <div className="appointment-header">
    <div>
      <span className="appointment-badge">
        ODASHA • APPOINTMENTS
      </span>

      <h2>
        {userRole === "patient"
          ? "My Appointments"
          : "Appointments"}
      </h2>

      <p>
        Keep track of your scheduled healthcare consultations.
      </p>
    </div>

    <div className="appointment-count">
      <span>{appointments.length}</span>
      <small>
        {appointments.length === 1
          ? "Appointment"
          : "Appointments"}
      </small>
    </div>
  </div>


  {loading ? (

    <div className="appointment-empty">
      <div className="appointment-loading-icon">
        ⏳
      </div>

      <p>Loading your appointments...</p>
    </div>

  ) : appointments.length === 0 ? (

    <div className="appointment-empty">

      <div className="appointment-empty-icon">
        📅
      </div>

      <h3>No appointments yet</h3>

      <p>
        Your scheduled appointments will appear here.
      </p>

    </div>

  ) : (

    <div className="appointment-list">

      {appointments.map((appointment) => (

        <div
          className="appointment-card"
          key={appointment.id}
        >

          <div className="appointment-card-top">

            <div className="appointment-doctor-icon">
              👨‍⚕️
            </div>

            <div className="appointment-doctor-info">

              <span className="appointment-label">
                CONSULTATION WITH
              </span>

              <h3>
                {appointment.doctor_name}
              </h3>

              {userRole !== "patient" && (
                <p>
                  Patient: {appointment.patient_name}
                </p>
              )}

            </div>

            <span className="appointment-status">
              Upcoming
            </span>

          </div>


          <div className="appointment-details">

            <div className="appointment-detail">

              <span className="detail-icon">
                📅
              </span>

              <div>
                <small>Date</small>

                <strong>
                  {appointment.appointment_date}
                </strong>
              </div>

            </div>


            <div className="appointment-detail">

              <span className="detail-icon">
                🕐
              </span>

              <div>
                <small>Time</small>

                <strong>
                  {appointment.appointment_time}
                </strong>
              </div>

            </div>

          </div>


          <div className="appointment-card-footer">

            <span>
              ✓ Appointment confirmed
            </span>

            <span>
              ID #{appointment.id}
            </span>

          </div>

        </div>

      ))}

    </div>

  )}

</div>

    </main>
  );
}

export default Appointments;