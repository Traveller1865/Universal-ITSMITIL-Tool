import React, { useEffect, useState } from 'react';

const IncidentOverview = () => {
  const [incidents, setIncidents] = useState([]);

  // Fetch incident data from backend
  useEffect(() => {
    fetch('/api/incidents') // Assuming your backend has this endpoint
      .then(response => response.json())
      .then(data => setIncidents(data))
      .catch(error => console.error('Error fetching incidents:', error));
  }, []);

  return (
    <div>
      <h2>Incident Overview</h2>
      <div className="incident-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Severity</th>
              <th>Status</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {incidents.map(incident => (
              <tr key={incident.id}>
                <td>{incident.id}</td>
                <td>{incident.severity}</td>
                <td>{incident.status}</td>
                <td>{incident.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default IncidentOverview;
