import { useEffect, useState } from "react";


function Patients() {

  const [patients, setPatients] = useState([]);

  const [name, setName] = useState("");
  const [age, setAge] = useState("");
  const [gender, setGender] = useState("");

  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [editingId, setEditingId] = useState(null);


  const fetchPatients = async () => {

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/patients/"
      );

      const data = await response.json();

      setPatients(data);

    } catch (error) {

      console.error("Error fetching patients:", error);

    }

    setLoading(false);
  };


  const startEdit = (patient) => {

    setEditingId(patient.id);

    setName(patient.name);

    setAge(patient.age);

    setGender(patient.gender);
  };


  useEffect(() => {

    fetchPatients();

  }, []);


  const addPatient = async (e) => {

  e.preventDefault();

  if (!name.trim() || !age || !gender) {
    return;
  }

  setAdding(true);

  try {

    let response;

    if (editingId) {

      // Update existing patient

      response = await fetch(
        `http://127.0.0.1:8000/patients/${editingId}`,
        {
          method: "PUT",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            name: name,
            age: Number(age),
            gender: gender
          })
        }
      );

    } else {

      // Create new patient

      response = await fetch(
        "http://127.0.0.1:8000/patients/",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            name: name,
            age: Number(age),
            gender: gender
          })
        }
      );

    }


    if (!response.ok) {

      throw new Error(
        editingId
          ? "Failed to update patient"
          : "Failed to add patient"
      );

    }


    // Clear form

    setName("");
    setAge("");
    setGender("");

    // Exit edit mode

    setEditingId(null);

    // Refresh patient list

    await fetchPatients();


  } catch (error) {

    console.error(
      "Error saving patient:",
      error
    );

  }


  setAdding(false);
};
const deletePatient = async (patientId) => {

  const confirmDelete = window.confirm(
    "Are you sure you want to delete this patient?"
  );

  if (!confirmDelete) {
    return;
  }

  try {

    const response = await fetch(
      `http://127.0.0.1:8000/patients/${patientId}`,
      {
        method: "DELETE"
      }
    );


    if (!response.ok) {
      throw new Error("Failed to delete patient");
    }


    await fetchPatients();


  } catch (error) {

    console.error(
      "Error deleting patient:",
      error
    );

  }
};


  return (

    <main className="page">

      <h2>Patients</h2>

      <p>
        Manage patient information.
      </p>


      {/* Add Patient Form */}

      <form
        className="patient-form"
        onSubmit={addPatient}
      >

        <input
          type="text"
          placeholder="Patient name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />


        <input
          type="number"
          placeholder="Age"
          value={age}
          onChange={(e) => setAge(e.target.value)}
        />


        <select
          value={gender}
          onChange={(e) => setGender(e.target.value)}
        >

          <option value="">
            Select gender
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


        <button
          type="submit"
          disabled={adding}
        >
          {adding ? "Adding..." : "Add Patient"}
        </button>

      </form>


      {/* Patient List */}

      {loading ? (

        <p>Loading patients...</p>

      ) : patients.length === 0 ? (

        <p>No patients found.</p>

      ) : (

        <div className="patient-list">

          {patients.map((patient) => (

            <div
              className="patient-card"
              key={patient.id}
            >

              <h3>
                {patient.name}
              </h3>

              <p>
                <strong>ID:</strong> {patient.id}
              </p>

              <p>
                <strong>Age:</strong> {patient.age}
              </p>

              <p>
                <strong>Gender:</strong> {patient.gender}
              </p>


              {/* Edit Button */}

              <button
                className="edit-button"
                onClick={() => startEdit(patient)}
              >
                Edit
              </button>
              <button
                className="delete-button"
                onClick={() => deletePatient(patient.id)}
                >
                Delete
                </button>

            </div>

          ))}

        </div>

      )}

    </main>

  );
}


export default Patients;