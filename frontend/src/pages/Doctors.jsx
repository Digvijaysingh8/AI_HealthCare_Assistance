import { useEffect, useState } from "react";


function Doctors() {

  const [doctors, setDoctors] = useState([]);

  const [name, setName] = useState("");
  const [specialization, setSpecialization] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [editingId, setEditingId] = useState(null);


  // Fetch all doctors

  const fetchDoctors = async () => {

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/doctors/"
      );

      const data = await response.json();

      setDoctors(data);

    } catch (error) {

      console.error(
        "Error fetching doctors:",
        error
      );

    }

    setLoading(false);
  };


  // Start editing a doctor

  const startEdit = (doctor) => {

    setEditingId(doctor.id);

    setName(doctor.name);

    setSpecialization(
      doctor.specialization
    );
  };


  // Load doctors when page opens

  useEffect(() => {

    fetchDoctors();

  }, []);


  // Add or update doctor

  const saveDoctor = async (e) => {

    e.preventDefault();


    if (
      !name.trim() ||
      !specialization.trim()
    ) {
      return;
    }


    setSaving(true);


    try {

      let response;


      // UPDATE

      if (editingId) {

        response = await fetch(
          `http://127.0.0.1:8000/doctors/${editingId}`,
          {
            method: "PUT",

            headers: {
              "Content-Type": "application/json"
            },

            body: JSON.stringify({
              name: name,
              specialization: specialization
            })
          }
        );

      }

      // ADD

      else {

        response = await fetch(
          "http://127.0.0.1:8000/doctors/",
          {
            method: "POST",

            headers: {
              "Content-Type": "application/json"
            },

            body: JSON.stringify({
              name: name,
              specialization: specialization
            })
          }
        );

      }


      if (!response.ok) {

        throw new Error(
          editingId
            ? "Failed to update doctor"
            : "Failed to add doctor"
        );

      }


      // Clear form

      setName("");

      setSpecialization("");

      // Exit edit mode

      setEditingId(null);

      // Refresh doctor list

      await fetchDoctors();


    } catch (error) {

      console.error(
        "Error saving doctor:",
        error
      );

    }


    setSaving(false);
  };


  // Delete doctor

  const deleteDoctor = async (doctorId) => {

    const confirmDelete = window.confirm(
      "Are you sure you want to delete this doctor?"
    );


    if (!confirmDelete) {
      return;
    }


    try {

      const response = await fetch(
        `http://127.0.0.1:8000/doctors/${doctorId}`,
        {
          method: "DELETE"
        }
      );


      if (!response.ok) {

        throw new Error(
          "Failed to delete doctor"
        );

      }


      // Refresh list

      await fetchDoctors();


    } catch (error) {

      console.error(
        "Error deleting doctor:",
        error
      );

    }
  };


  // Cancel editing

  const cancelEdit = () => {

    setEditingId(null);

    setName("");

    setSpecialization("");
  };


  return (

    <main className="page">

      <h2>Doctors</h2>

      <p>
        Manage doctor information.
      </p>


      {/* Add / Update Doctor Form */}

      <form
        className="doctor-form"
        onSubmit={saveDoctor}
      >

        <input
          type="text"
          placeholder="Doctor name"
          value={name}
          onChange={(e) =>
            setName(e.target.value)
          }
        />


        <input
          type="text"
          placeholder="Specialization"
          value={specialization}
          onChange={(e) =>
            setSpecialization(
              e.target.value
            )
          }
        />


        <button
          type="submit"
          disabled={saving}
        >

          {saving
            ? (
              editingId
                ? "Updating..."
                : "Adding..."
            )
            : (
              editingId
                ? "Update Doctor"
                : "Add Doctor"
            )
          }

        </button>


        {/* Cancel button */}

        {editingId && (

          <button
            type="button"
            className="cancel-button"
            onClick={cancelEdit}
          >
            Cancel
          </button>

        )}

      </form>


      {/* Doctor List */}

      {loading ? (

        <p>Loading doctors...</p>

      ) : doctors.length === 0 ? (

        <p>No doctors found.</p>

      ) : (

        <div className="doctor-list">

          {doctors.map((doctor) => (

            <div
              className="doctor-card"
              key={doctor.id}
            >

              <h3>
                {doctor.name}
              </h3>


              <p>
                <strong>ID:</strong>{" "}
                {doctor.id}
              </p>


              <p>
                <strong>
                  Specialization:
                </strong>{" "}
                {doctor.specialization}
              </p>


              {/* Action Buttons */}

              <div className="doctor-actions">

                <button
                  className="edit-button"
                  onClick={() =>
                    startEdit(doctor)
                  }
                >
                  Edit
                </button>


                <button
                  className="delete-button"
                  onClick={() =>
                    deleteDoctor(doctor.id)
                  }
                >
                  Delete
                </button>

              </div>

            </div>

          ))}

        </div>

      )}

    </main>

  );
}


export default Doctors;