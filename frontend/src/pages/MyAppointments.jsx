import { useEffect, useState } from "react";

function MyAppointments() {

  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  /*
    ------------------------------------------------
    SCROLL TO MY APPOINTMENTS PAGE
    ------------------------------------------------

    When My Appointments opens:

    1. Find the blue header
    2. Get its exact height
    3. Scroll the browser by that height

    Result:
    The blue header goes completely above the screen
    and the My Appointments page starts at the top.
  */

  useEffect(() => {

    const scrollToAppointments = () => {

      const header =
        document.querySelector(".header");

      const headerHeight =
        header?.offsetHeight || 0;

      window.scrollTo({
        top: headerHeight,
        left: 0,
        behavior: "auto"
      });

    };

    /*
      Wait until the page has finished rendering.
    */

    requestAnimationFrame(() => {

      requestAnimationFrame(() => {

        scrollToAppointments();

      });

    });

  }, []);


  /*
    ------------------------------------------------
    FETCH APPOINTMENTS
    ------------------------------------------------
  */

  useEffect(() => {

    const fetchAppointments = async () => {

      const token =
        localStorage.getItem("access_token");

      try {

        const response = await fetch(
          "http://127.0.0.1:8000/appointments/my",
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        const data =
          await response.json();

        if (!response.ok) {

          throw new Error(
            data.detail ||
            "Failed to fetch appointments"
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


  /*
    ------------------------------------------------
    LOADING
    ------------------------------------------------
  */

  if (loading) {

    return (

      <main className="my-appointments-page">

        <div className="appointments-loading">

          <div className="loading-icon">
            ⏳
          </div>

          <h2>
            Loading your appointments...
          </h2>

          <p>
            Please wait while we fetch your
            appointments.
          </p>

        </div>

      </main>

    );

  }


  /*
    ------------------------------------------------
    ERROR
    ------------------------------------------------
  */

  if (error) {

    return (

      <main className="my-appointments-page">

        <div className="appointments-error">

          <div className="error-icon">
            !
          </div>

          <h2>
            Unable to load appointments
          </h2>

          <p>
            {error}
          </p>

        </div>

      </main>

    );

  }


  /*
    ------------------------------------------------
    MAIN PAGE
    ------------------------------------------------
  */

  return (

    <main className="my-appointments-page">


      {/* =========================================
          HERO
          ========================================= */}

      <section className="my-appointments-hero">

        <span className="appointments-badge">
          ODASHA • MY HEALTHCARE
        </span>

        <h2>
          My Appointments
        </h2>

        <p>
          Keep track of your upcoming healthcare
          consultations in one place.
        </p>

      </section>


      {/* =========================================
          APPOINTMENT COUNT
          ========================================= */}

      <div className="appointments-summary">

        <div className="summary-icon">
          📅
        </div>

        <div>

          <strong>
            {appointments.length}
          </strong>

          <span>

            {appointments.length === 1
              ? "Scheduled Appointment"
              : "Scheduled Appointments"}

          </span>

        </div>

      </div>


      {/* =========================================
          APPOINTMENTS
          ========================================= */}

      {appointments.length === 0 ? (

        <section className="no-appointments">

          <div className="empty-icon">
            📅
          </div>

          <h3>
            No appointments yet
          </h3>

          <p>
            You don't have any appointments scheduled.
          </p>

        </section>

      ) : (

        <section className="my-appointments-list">

          {appointments.map(
            (appointment) => (

              <article
                className="my-appointment-card"
                key={appointment.id}
              >


                {/* =================================
                    CARD HEADER
                    ================================= */}

                <div className="appointment-card-header">

                  <div className="doctor-avatar">
                    👨‍⚕️
                  </div>


                  <div className="doctor-info">

                    <span>
                      CONSULTATION WITH
                    </span>

                    <h3>
                      {appointment.doctor_name}
                    </h3>

                  </div>


                  <div className="appointment-status">
                    ✓ Confirmed
                  </div>

                </div>


                {/* =================================
                    DETAILS
                    ================================= */}

                <div className="appointment-card-details">


                  {/* DATE */}

                  <div className="appointment-detail-box">

                    <div className="detail-icon">
                      📅
                    </div>

                    <div>

                      <span>
                        DATE
                      </span>

                      <strong>
                        {appointment.appointment_date}
                      </strong>

                    </div>

                  </div>


                  {/* TIME */}

                  <div className="appointment-detail-box">

                    <div className="detail-icon">
                      🕐
                    </div>

                    <div>

                      <span>
                        TIME
                      </span>

                      <strong>
                        {appointment.appointment_time}
                      </strong>

                    </div>

                  </div>

                </div>


                {/* =================================
                    FOOTER
                    ================================= */}

                <div className="appointment-card-footer">

                  <span>
                    ✓ Your appointment is scheduled
                  </span>

                  <span>
                    Appointment #{appointment.id}
                  </span>

                </div>


              </article>

            )
          )}

        </section>

      )}

    </main>

  );

}

export default MyAppointments;