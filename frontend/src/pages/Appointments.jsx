import { useEffect, useState } from "react";
import DatePicker from "react-datepicker";

import "react-datepicker/dist/react-datepicker.css";


function Appointments() {
  const [availableSlots, setAvailableSlots] = useState([]);
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [patients, setPatients] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [appointments, setAppointments] = useState([]);

  const [patientId, setPatientId] = useState("");
  const [doctorId, setDoctorId] = useState("");

  const [appointmentDate, setAppointmentDate] = useState("");
  const [appointmentTime, setAppointmentTime] = useState("");

  const [newPatient, setNewPatient] = useState(false);

  const [patientName, setPatientName] = useState("");
  const [patientAge, setPatientAge] = useState("");
  const [patientGender, setPatientGender] = useState("");

  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);


 const fetchData = async () => {

  setLoading(true);

  try {

    const patientsResponse = await fetch(
      "http://127.0.0.1:8000/patients/"
    );

    if (!patientsResponse.ok) {
      throw new Error("Failed to fetch patients");
    }

    const patientsData =
      await patientsResponse.json();

    setPatients(patientsData);


    const doctorsResponse = await fetch(
      "http://127.0.0.1:8000/doctors/"
    );

    if (!doctorsResponse.ok) {
      throw new Error("Failed to fetch doctors");
    }

    const doctorsData =
      await doctorsResponse.json();

    setDoctors(doctorsData);


    const appointmentsResponse = await fetch(
      "http://127.0.0.1:8000/appointments/"
    );

    if (!appointmentsResponse.ok) {
      throw new Error("Failed to fetch appointments");
    }

    const appointmentsData =
      await appointmentsResponse.json();

    setAppointments(appointmentsData);


  } catch (error) {

    console.error(
      "Error fetching appointment data:",
      error
    );

  } finally {

    setLoading(false);

  }
};


  useEffect(() => {

    fetchData();

  }, []);
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

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Failed to fetch available slots"
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

  }

  setLoadingSlots(false);
  };

  const resetForm = () => {

    setPatientId("");
    setDoctorId("");
    setAppointmentDate("");
    setAppointmentTime("");

    setNewPatient(false);

    setPatientName("");
    setPatientAge("");
    setPatientGender("");
  };


  const bookAppointment = async (e) => {

    e.preventDefault();


    if (
      !doctorId ||
      !appointmentDate ||
      !appointmentTime
    ) {
      alert("Please fill all appointment details.");
      return;
    }


    if (newPatient) {

      if (
        !patientName.trim() ||
        !patientAge ||
        !patientGender
      ) {
        alert("Please fill all patient information.");
        return;
      }

    } else {

      if (!patientId) {
        alert("Please select a patient.");
        return;
      }

    }


    setBooking(true);


    try {

      let selectedPatientId = patientId;


      /*
        If user is adding a new patient,
        create the patient first.
      */

      if (newPatient) {

        const patientResponse = await fetch(
          "http://127.0.0.1:8000/patients/",
          {
            method: "POST",

            headers: {
              "Content-Type": "application/json"
            },

            body: JSON.stringify({
              name: patientName,
              age: Number(patientAge),
              gender: patientGender
            })
          }
        );


        const patientData =
          await patientResponse.json();


        if (!patientResponse.ok) {

          throw new Error(
            patientData.detail ||
            "Failed to create patient"
          );

        }


        selectedPatientId = patientData.id;
      }


      /*
        Now create the appointment.
      */

      const appointmentResponse = await fetch(
        "http://127.0.0.1:8000/appointments/",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            patient_id: Number(selectedPatientId),
            doctor_id: Number(doctorId),
            appointment_date: appointmentDate,
            appointment_time: appointmentTime
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

    }


    setBooking(false);
  };


  return (

    <main className="page">

      <h2>Book an Appointment</h2>

      <p>
        Schedule a consultation with one of our available doctors.
      </p>


      <form
        className="appointment-form"
        onSubmit={bookAppointment}
      >

        {/* PATIENT SECTION */}

        <div className="appointment-section-title">

          <h3>
            Patient Information
          </h3>

        </div>


        <div className="form-group">

          <label>
            Patient
          </label>


          {!newPatient ? (

            <select
              value={patientId}
              onChange={(e) =>
                setPatientId(e.target.value)
              }
            >

              <option value="">
                Select Patient
              </option>

              {patients.map((patient) => (

                <option
                  key={patient.id}
                  value={patient.id}
                >
                  {patient.name}
                </option>

              ))}

            </select>

          ) : (

            <input
              type="text"
              placeholder="Patient name"
              value={patientName}
              onChange={(e) =>
                setPatientName(e.target.value)
              }
            />

          )}

        </div>


        <div className="new-patient-container">

          <button
            type="button"
            className="new-patient-button"
            onClick={() => {

              setNewPatient(!newPatient);

              setPatientId("");

              setPatientName("");
              setPatientAge("");
              setPatientGender("");

            }}
          >

            {newPatient
              ? "← Select Existing Patient"
              : "+ Add New Patient"
            }

          </button>

        </div>


        {newPatient && (

          <>

            <div className="form-group">

              <label>
                Age
              </label>

              <input
                type="number"
                placeholder="Patient age"
                value={patientAge}
                onChange={(e) =>
                  setPatientAge(e.target.value)
                }
              />

            </div>


            <div className="form-group">

              <label>
                Gender
              </label>

              <select
                value={patientGender}
                onChange={(e) =>
                  setPatientGender(e.target.value)
                }
              >

                <option value="">
                  Select Gender
                </option>

                <option value="Male">
                  Male
                </option>

                <option value="Female">
                  Female
                </option>

                <option value="Other">
                  Other
                </option>

              </select>

            </div>

          </>

        )}


        {/* APPOINTMENT SECTION */}

        <div className="appointment-section-title">

          <h3>
            Appointment Details
          </h3>

        </div>


        <div className="form-group">

          <label>
            Doctor
          </label>

          <select
            value={doctorId}
            onChange={(e) =>
              setDoctorId(e.target.value)
            }
          >

            <option value="">
              Select Doctor
            </option>

            {doctors.map((doctor) => (

              <option
                key={doctor.id}
                value={doctor.id}
              >
                {doctor.name} - {doctor.specialization}
              </option>

            ))}

          </select>

        </div>


<div className="form-group">
  <label>Appointment Date</label>

  <DatePicker
    selected={
      appointmentDate
        ? new Date(appointmentDate + "T00:00:00")
        : null
    }
    onChange={(date) => {

      if (!date) {
        setAppointmentDate("");
        return;
      }

      const year = date.getFullYear();

      const month = String(
        date.getMonth() + 1
      ).padStart(2, "0");

      const day = String(
        date.getDate()
      ).padStart(2, "0");

      setAppointmentDate(
        `${year}-${month}-${day}`
      );
    }}
    minDate={new Date()}
    dateFormat="dd-MM-yyyy"
    placeholderText="Select appointment date"
    className="appointment-date-picker"
  />
</div>




<div className="form-group">
  <label>Appointment Time</label>

  {!doctorId || !appointmentDate ? (

    <p>
      Please select a doctor and date first.
    </p>

  ) : loadingSlots ? (

    <p>
      Loading available slots...
    </p>

  ) : availableSlots.length === 0 ? (

    <p>
      No available slots for this date.
    </p>

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


        <button
          type="submit"
          disabled={booking || loading}
        >

          {booking
            ? "Booking..."
            : "Book Appointment"
          }

        </button>

      </form>


      {/* EXISTING APPOINTMENTS */}

      <div className="appointment-section">

        <h2>
          Appointments
        </h2>


        {loading ? (

          <p>
            Loading appointments...
          </p>

        ) : appointments.length === 0 ? (

          <p>
            No appointments found.
          </p>

        ) : (

          <div className="appointment-list">

            {appointments.map((appointment) => (

              <div
                className="appointment-card"
                key={appointment.id}
              >

                <h3>
                  {appointment.patient_name}
                </h3>

                <p>
                  <strong>
                    Doctor:
                  </strong>{" "}
                  {appointment.doctor_name}
                </p>

                <p>
                  <strong>
                    Date:
                  </strong>{" "}
                  {appointment.appointment_date}
                </p>

                <p>
                  <strong>
                    Time:
                  </strong>{" "}
                  {appointment.appointment_time}
                </p>

              </div>

            ))}

          </div>

        )}

      </div>

    </main>

  );
}


export default Appointments;