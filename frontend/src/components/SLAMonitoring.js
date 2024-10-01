import React, { useState, useEffect } from 'react';

const SLAMonitoring = () => {
  const [incidents, setIncidents] = useState([]);
  const [error, setError] = useState(''); // Error state
  const [loading, setLoading] = useState(true); // Loading state

  useEffect(() => {
    const token = localStorage.getItem('token'); // Get the token from localStorage

    if (!token) {
      setError('No authentication token found. Please log in.'); // Error if no token found
      setLoading(false); // Stop loading if no token
      return;
    }

    // Fetch incidents for SLA monitoring from backend with authorization header
    fetch('/api/incidents/sla-monitor', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`, // Add token to Authorization header
        'Content-Type': 'application/json',
      },
    })
    .then(response => {
      console.log('SLA Monitoring Response:', response); // Log the response for debugging

      const contentType = response.headers.get('content-type');
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Unauthorized. Please log in again.');
        }
        throw new Error('Failed to fetch SLA data');
      }

      // Check if the response is JSON and parse accordingly
      if (contentType && contentType.includes('application/json')) {
        return response.json();  // Only parse JSON if content-type is application/json
      } else {
        // Log what kind of response was received (useful for debugging)
        console.error("Non-JSON response received:", response);
        throw new Error('Received non-JSON response from server');
      }
    })
    .then(data => {
      setIncidents(data);
      setLoading(false);
      setError(''); // Clear any previous errors
    })
    .catch(error => {
      console.error('Error fetching SLA data:', error); // Log error to console
      setError(error.message || 'Failed to load SLA data. Please try again.'); // Set error message
      setLoading(false);
    });
}, []); // Empty dependency array ensures this runs once on component mount


  if (loading) return <p>Loading SLA data...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h2>SLA Monitoring</h2>
      <div className="sla-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Incident Name</th>
              <th>Priority</th>
              <th>SLA Breach</th>
              <th>Time Remaining</th>
            </tr>
          </thead>
          <tbody>
            {incidents.map(incident => (
              <tr key={incident.id}>
                <td>{incident.id}</td>
                <td>{incident.name}</td>
                <td>{incident.priority}</td>
                <td>{incident.is_sla_breached ? 'Breached' : 'Within SLA'}</td>
                <td>{incident.time_remaining || 'N/A'}</td> {/* Fallback if time_remaining is missing */}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SLAMonitoring;
