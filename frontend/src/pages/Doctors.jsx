import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function Doctors() {
  const navigate = useNavigate();

  const [expandedDoctor, setExpandedDoctor] = useState(null);

  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const doctorProfiles = [
    {
      specialization: "Cardiologist",
      qualification: "MBBS, MD, DM Cardiology",
      experience: "12+ years experience",
      rating: "4.9",
      description:
        "Specializes in preventive cardiology, heart health and cardiovascular care.",
      nature:
        "Calm, patient-focused and attentive.",
      specializations: [
        "Preventive Cardiology",
        "Heart Health",
        "Cardiovascular Care"
      ]
    },

    {
      specialization: "Dermatologist",
      qualification: "MBBS, MD Dermatology",
      experience: "9+ years experience",
      rating: "4.8",
      description:
        "Focused on clinical dermatology, skin conditions and long-term skin health.",
      nature:
        "Friendly, approachable and detail-oriented.",
      specializations: [
        "Clinical Dermatology",
        "Skin Conditions",
        "Skin Health"
      ]
    },

    {
      specialization: "Neurologist",
      qualification: "MBBS, MD, DM Neurology",
      experience: "14+ years experience",
      rating: "4.9",
      description:
        "Provides neurological evaluation and care for a wide range of nervous-system conditions.",
      nature:
        "Thoughtful, analytical and patient-focused.",
      specializations: [
        "Neurological Evaluation",
        "Brain Health",
        "Nervous-System Care"
      ]
    },

    {
      specialization: "Pediatrician",
      qualification: "MBBS, MD Pediatrics",
      experience: "10+ years experience",
      rating: "4.8",
      description:
        "Provides healthcare support focused on children's growth, development and general health.",
      nature:
        "Warm, caring and comfortable with young patients.",
      specializations: [
        "Child Healthcare",
        "Growth & Development",
        "Pediatric Care"
      ]
    },

    {
      specialization: "Orthopedic Specialist",
      qualification: "MBBS, MS Orthopedics",
      experience: "11+ years experience",
      rating: "4.7",
      description:
        "Focused on musculoskeletal conditions, joint health and orthopedic care.",
      nature:
        "Practical, supportive and straightforward.",
      specializations: [
        "Joint Health",
        "Musculoskeletal Care",
        "Orthopedic Evaluation"
      ]
    },

    {
      specialization: "Gynecologist",
      qualification: "MBBS, MD Obstetrics & Gynecology",
      experience: "13+ years experience",
      rating: "4.9",
      description:
        "Provides women's healthcare and reproductive health services.",
      nature:
        "Compassionate, respectful and attentive.",
      specializations: [
        "Women's Healthcare",
        "Reproductive Health",
        "Gynecological Care"
      ]
    },

    {
      specialization: "General Physician",
      qualification: "MBBS, MD General Medicine",
      experience: "15+ years experience",
      rating: "4.8",
      description:
        "Provides general medical evaluation, preventive care and routine healthcare.",
      nature:
        "Patient, approachable and thorough.",
      specializations: [
        "General Medicine",
        "Preventive Care",
        "Routine Healthcare"
      ]
    },

    {
      specialization: "Endocrinologist",
      qualification: "MBBS, MD, DM Endocrinology",
      experience: "10+ years experience",
      rating: "4.8",
      description:
        "Focused on diabetes, thyroid disorders and metabolic health.",
      nature:
        "Clear, supportive and evidence-focused.",
      specializations: [
        "Diabetes Care",
        "Thyroid Disorders",
        "Metabolic Health"
      ]
    },

    {
      specialization: "Gastroenterologist",
      qualification: "MBBS, MD, DM Gastroenterology",
      experience: "12+ years experience",
      rating: "4.7",
      description:
        "Focused on digestive health and gastrointestinal conditions.",
      nature:
        "Calm, informative and attentive.",
      specializations: [
        "Digestive Health",
        "Gastrointestinal Care",
        "Digestive Disorders"
      ]
    },

    {
      specialization: "Psychiatrist",
      qualification: "MBBS, MD Psychiatry",
      experience: "8+ years experience",
      rating: "4.9",
      description:
        "Provides mental-health evaluation and supportive healthcare.",
      nature:
        "Empathetic, patient and non-judgmental.",
      specializations: [
        "Mental Health",
        "Psychiatric Evaluation",
        "Supportive Care"
      ]
    }
  ];


  /*
    =========================================
    FETCH DOCTORS
    =========================================
  */

  useEffect(() => {

    const fetchDoctors = async () => {

      try {

        const response = await fetch(
          "http://127.0.0.1:8000/doctors/"
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail || "Failed to fetch doctors"
          );
        }

        setDoctors(data);

      } catch (error) {

        setError(error.message);

      } finally {

        setLoading(false);

      }

    };

    fetchDoctors();

  }, []);


  /*
    =========================================
    STOP BACKGROUND SCROLL WHEN MODAL OPENS
    =========================================
  */

  useEffect(() => {

    if (expandedDoctor !== null) {

      document.body.style.overflow = "hidden";

    } else {

      document.body.style.overflow = "";

    }

    return () => {
      document.body.style.overflow = "";
    };

  }, [expandedDoctor]);


  /*
    =========================================
    CLOSE MODAL WITH ESC
    =========================================
  */

  useEffect(() => {

    const handleEscape = (event) => {

      if (event.key === "Escape") {
        setExpandedDoctor(null);
      }

    };

    window.addEventListener(
      "keydown",
      handleEscape
    );

    return () => {

      window.removeEventListener(
        "keydown",
        handleEscape
      );

    };

  }, []);


  /*
    =========================================
    LOADING
    =========================================
  */

  if (loading) {

    return (
      <main className="doctors-page">

        <div className="doctors-loading">
          Loading doctors...
        </div>

      </main>
    );

  }


  /*
    =========================================
    ERROR
    =========================================
  */

  if (error) {

    return (
      <main className="doctors-page">

        <div className="doctors-error">
          {error}
        </div>

      </main>
    );

  }


  /*
    =========================================
    MAIN PAGE
    =========================================
  */

  return (

    <main className="doctors-page">

      {/* =====================================
          PAGE HEADER
          ===================================== */}

      <section className="doctors-hero">

        <span className="doctors-badge">
          ODASHA • OUR SPECIALISTS
        </span>

        <h2>
          Find the right doctor for you
        </h2>

        <p>
          Explore our healthcare specialists,
          understand their areas of expertise,
          and book an appointment with a doctor.
        </p>

      </section>


      {/* =====================================
          DOCTOR CARDS
          ===================================== */}

      <section className="doctors-grid">

        {doctorProfiles.map((profile, index) => {

          const databaseDoctor =
            doctors[index];

          const doctorName =
            databaseDoctor?.name ||
            `Dr. ${profile.specialization}`;

          const doctorId =
            databaseDoctor?.id || null;


          return (

            <article
              className="doctor-card"
              key={index}
            >

              <div className="doctor-card-main">


                {/* AVATAR */}

                <div className="doctor-avatar">

                  {doctorName
                    .replace("Dr. ", "")
                    .charAt(0)
                    .toUpperCase()}

                </div>


                {/* CONTENT */}

                <div className="doctor-card-content">


                  <div className="doctor-title-row">

                    <div>

                      <h3>
                        {doctorName}
                      </h3>

                      <p className="doctor-specialization">
                        {profile.specialization}
                      </p>

                    </div>


                    <div className="doctor-rating">
                      ★ {profile.rating}
                    </div>

                  </div>


                  <p className="doctor-qualification">
                    {profile.qualification}
                  </p>


                  <p className="doctor-experience">
                    {profile.experience}
                  </p>


                  <p className="doctor-description">
                    {profile.description}
                  </p>


                  <p className="doctor-nature">

                    <strong>
                      Approach:
                    </strong>{" "}

                    {profile.nature}

                  </p>


                  {/* BUTTONS */}

                  <div className="doctor-card-actions">


                    <button
                      type="button"
                      className="doctor-view-button"
                      onClick={() => {

                        setExpandedDoctor(index);

                      }}
                    >
                      View Full Profile
                    </button>


                    <button
                      type="button"
                      className="doctor-book-button"
                      disabled={!doctorId}
                      onClick={(event) => {

                        event.stopPropagation();

                        if (!doctorId) {
                          return;
                        }

                        navigate(
                          "/appointments",
                          {
                            state: {
                              doctorId:
                                doctorId,

                              doctorName:
                                doctorName
                            }
                          }
                        );

                      }}
                    >
                      Book Appointment
                    </button>


                  </div>

                </div>

              </div>

            </article>

          );

        })}

      </section>


      {/* =====================================
          DOCTOR PROFILE MODAL
          ===================================== */}

      {expandedDoctor !== null && (() => {

        const profile =
          doctorProfiles[expandedDoctor];

        if (!profile) {
          return null;
        }

        const databaseDoctor =
          doctors[expandedDoctor];

        const doctorName =
          databaseDoctor?.name ||
          `Dr. ${profile.specialization}`;

        const doctorId =
          databaseDoctor?.id || null;


        return (

          <div
            className="doctor-profile-overlay"
            onClick={() => {

              setExpandedDoctor(null);

            }}
          >


            <div
              className="doctor-profile-modal"
              onClick={(event) => {

                event.stopPropagation();

              }}
            >


              {/* CLOSE */}

              <button
                type="button"
                className="doctor-modal-close"
                onClick={() => {

                  setExpandedDoctor(null);

                }}
              >
                ×
              </button>


              {/* =================================
                  MODAL HEADER
                  ================================= */}

              <div className="doctor-modal-header">


                <div className="doctor-modal-avatar">

                  {doctorName
                    .replace("Dr. ", "")
                    .charAt(0)
                    .toUpperCase()}

                </div>


                <div className="doctor-modal-name">

                  <span>
                    ODASHA SPECIALIST
                  </span>

                  <h2>
                    {doctorName}
                  </h2>

                  <p>
                    {profile.specialization}
                  </p>

                </div>


                <div className="doctor-modal-rating">
                  ★ {profile.rating}
                </div>

              </div>


              {/* =================================
                  ABOUT
                  ================================= */}

              <div className="doctor-modal-section">

                <h3>
                  About the Doctor
                </h3>

                <p>
                  {profile.description}{" "}
                  This doctor focuses on providing
                  personalized healthcare and helping
                  patients understand their treatment
                  options and long-term health goals.
                </p>

              </div>


              {/* =================================
                  DETAILS
                  ================================= */}

              <div className="doctor-modal-details">


                <div className="doctor-modal-detail">

                  <span>
                    Qualification
                  </span>

                  <strong>
                    {profile.qualification}
                  </strong>

                </div>


                <div className="doctor-modal-detail">

                  <span>
                    Experience
                  </span>

                  <strong>
                    {profile.experience}
                  </strong>

                </div>


                <div className="doctor-modal-detail">

                  <span>
                    Specialization
                  </span>

                  <strong>
                    {profile.specialization}
                  </strong>

                </div>


                <div className="doctor-modal-detail">

                  <span>
                    Patient Approach
                  </span>

                  <strong>
                    {profile.nature}
                  </strong>

                </div>

              </div>


              {/* =================================
                  AREAS OF FOCUS
                  ================================= */}

              <div className="doctor-modal-section">

                <h3>
                  Areas of Focus
                </h3>


                <div className="doctor-modal-tags">

                  {(profile.specializations || []).map(
                    (item, itemIndex) => (

                      <span
                        key={itemIndex}
                      >
                        {item}
                      </span>

                    )
                  )}

                </div>

              </div>


              {/* =================================
                  ACTIONS
                  ================================= */}

              <div className="doctor-modal-actions">


                <button
                  type="button"
                  className="doctor-modal-book"
                  disabled={!doctorId}
                  onClick={() => {

                    if (!doctorId) {
                      return;
                    }

                    navigate(
                      "/appointments",
                      {
                        state: {
                          doctorId:
                            doctorId,

                          doctorName:
                            doctorName
                        }
                      }
                    );

                  }}
                >
                  Book Appointment
                </button>


                <button
                  type="button"
                  className="doctor-modal-cancel"
                  onClick={() => {

                    setExpandedDoctor(null);

                  }}
                >
                  Close Profile
                </button>


              </div>


            </div>

          </div>

        );

      })()}

    </main>

  );
}

export default Doctors;