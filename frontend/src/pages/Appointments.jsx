import { useEffect, useState } from "react";


function Appointments() {

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

    try {

      const patientsResponse = await fetch(
        "http://127.0.0.1:8000/patients/"
      );

      const doctorsResponse = await fetch(
        "http://127.0.0.1:8000/doctors/"
      );

      const appointmentsResponse = await fetch(
        "http://127.0.0.1:8000/appointments/"
      );


      const patientsData = await patientsResponse.json();
      const doctorsData = await doctorsResponse.json();
      const appointmentsData = await appointmentsResponse.json();


      setPatients(patientsData);
      setDoctors(doctorsData);
      setAppointments(appointmentsData);


    } catch (error) {

      console.error(
        "Error fetching appointment data:",
        error
      );

    }


    setLoading(false);
  };


  useEffect(() => {

    fetchData();

  }, []);


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

        <label>
            Appointment Date
        </label>

        <div className="date-input-container">

            <input
            type="date"
            value={appointmentDate}
            min={new Date().toISOString().split("T")[0]}
            onChange={(e) =>
                setAppointmentDate(e.target.value)
            }
            />

        </div>

        </div>


        <div className="form-group">

          <label>
            Appointment Time
          </label>

          <input
            type="time"
            value={appointmentTime}
            onChange={(e) =>
              setAppointmentTime(e.target.value)
            }
          />

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