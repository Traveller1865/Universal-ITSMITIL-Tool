import React, { useEffect, useState } from 'react';

const SLAMonitor = () => {
    const [violations, setViolations] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSLAViolations = async () => {
            const token = localStorage.getItem('token');
            try {
                const response = await fetch('http://localhost:5000/api/incidents/sla-monitor', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                const data = await response.json();
                setViolations(data);
                setLoading(false);
            } catch (error) {
                console.error('Error fetching SLA violations:', error);
                setLoading(false);
            }
        };

        fetchSLAViolations();
    }, []);

    if (loading) {
        return <p>Loading SLA violations...</p>;
    }

    return (
        <div>
            <h2>SLA Violations</h2>
            {violations.length > 0 ? (
                <ul>
                    {violations.map((violation) => (
                        <li key={violation.id}>
                            Incident {violation.name} (Priority: {violation.priority}) is nearing
                            {violation.nearing_acknowledgment ? ' acknowledgment' : ''}
                            {violation.nearing_resolution ? ' resolution' : ''} SLA breach.
                        </li>
                    ))}
                </ul>
            ) : (
                <p>No SLA violations detected.</p>
            )}
        </div>
    );
};

export default SLAMonitor;
