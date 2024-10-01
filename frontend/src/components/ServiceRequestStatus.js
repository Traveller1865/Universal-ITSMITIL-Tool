import React, { useState, useEffect } from 'react';

const ServiceRequestStatus = () => {
  const [requests, setRequests] = useState([]);
  const [statusFilter, setStatusFilter] = useState('Pending');
  const [error, setError] = useState(''); // Error state
  const [loading, setLoading] = useState(true); // Loading state

  useEffect(() => {
    const token = localStorage.getItem('token'); // Get the token from localStorage

    if (!token) {
      setError('No authentication token found. Please log in.'); // Error if no token found
      return;
    }

    // Fetch service request data from backend with authorization header
    fetch('http://localhost:5000/api/service-requests', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`, // Add token to Authorization header
        'Content-Type': 'application/json',
      },
    })
      .then(response => {
        console.log('Service Request Response:', response); // Log the response for debugging
        if (!response.ok) {
          throw new Error('Failed to fetch service requests');
        }
        return response.json();
      })
      .then(data => {
        setRequests(data);
        setLoading(false);
        setError(''); // Clear any previous errors
      })
      .catch(error => {
        console.error('Error fetching service requests:', error); // Log error to console
        setError('Failed to load service requests. Please try again.'); // Set error message
        setLoading(false);
      });
  }, []); // Empty dependency array ensures this runs once on component mount

  // Filter requests based on status
  const filteredRequests = requests.filter(request => request.status === statusFilter);

  if (loading) return <p>Loading service requests...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h2>Service Request Status</h2>
      <button onClick={() => setStatusFilter('Pending')}>Pending</button>
      <button onClick={() => setStatusFilter('Resolved')}>Resolved</button>

      <div className="service-request-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Request Type</th>
              <th>Requestor</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredRequests.map(request => (
              <tr key={request.id}>
                <td>{request.id}</td>
                <td>{request.type}</td>
                <td>{request.requestor}</td>
                <td>{request.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ServiceRequestStatus;
