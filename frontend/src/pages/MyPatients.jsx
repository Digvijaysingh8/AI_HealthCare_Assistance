import { useEffect, useState } from "react";

function MyPatients() {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPatients = async () => {
      const token = localStorage.getItem("access_token");

      try {
        const response = await fetch(
          "http://127.0.0.1:8000/doctors/my-patients",
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(
            data.detail || "Failed to fetch patients"
          );
        }

        setPatients(data);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPatients();
  }, []);

  if (loading) {
    return <p>Loading patients...</p>;
  }

  if (error) {
    return <p>{error}</p>;
  }

  return (
    <div>
      <h2>My Patients</h2>

      {patients.length === 0 ? (
        <p>No patients found.</p>
      ) : (
        patients.map((patient) => (
          <div key={patient.id}>
            <p>
              <strong>Name:</strong> {patient.name}
            </p>

            <p>
              <strong>Age:</strong> {patient.age}
            </p>

            <p>
              <strong>Gender:</strong> {patient.gender}
            </p>

            <hr />
          </div>
        ))
      )}
    </div>
  );
}

export default MyPatients;