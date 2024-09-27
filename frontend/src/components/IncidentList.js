import React, { useEffect, useState } from 'react';

const IncidentList = () => {
    const [incidents, setIncidents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('');

    // Fetch incidents from the backend
    useEffect(() => {
        const fetchIncidents = async () => {
            try {
                const response = await fetch('http://localhost:5000/api/incidents');
                if (!response.ok) {
                    throw new Error('Failed to fetch incidents');
                }
                const data = await response.json();
                setIncidents(data);
                setLoading(false);
            } catch (error) {
                setError(error.message);
                setLoading(false);
            }
        };
        fetchIncidents();
    }, []);

    // Handle search and filter
    const filteredIncidents = incidents.filter((incident) => {
        return ( 
            incident.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
            (categoryFilter === '' || incident.category === categoryFilter)
        );
    })

    // Render the loading state
    if (loading) {
        return <p>Loading incidents...</p>;
    }

   // Render the error state
   if (error) {
    return <p>{error}</p>;
}

return (
    <div className="incident-list">
        <h2>Incident List</h2>

        {/* Search and Filter */}
        <div className="filters">
            <input
                type="text"
                placeholder="Search by name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
            />
            <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
            >
                <option value="">All Categories</option>
                <option value="Hardware">Hardware</option>
                <option value="Software">Software</option>
                <option value="Network">Network</option>
            </select>
        </div>

        {filteredIncidents.length > 0 ? (
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Description</th>
                        <th>Category</th>
                    </tr>
                </thead>
                <tbody>
                    {filteredIncidents.map((incident) => (
                        <tr key={incident.id}>
                            <td>{incident.id}</td>
                            <td>{incident.name}</td>
                            <td>{incident.email}</td>
                            <td>{incident.description}</td>
                            <td>{incident.category}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        ) : (
            <p>No incidents found.</p>
        )}
    </div>
);
};

export default IncidentList;