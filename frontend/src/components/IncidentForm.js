import React, { useState } from 'react';
import '../Styles/IncidentForm.css'; // Import the CSS file

const IncidentForm = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        description: '',
        category: 'Hardware',
    });

    const [responseMessage, setResponseMessage] = useState('');
    const [error, setError] = useState(false);  // Track error state
    const [loading, setLoading] = useState(false);  // Track loading state

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);  // Show loading spinner during submission
        try {
            const response = await fetch('http://localhost:5000/api/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                const result = await response.json();
                setResponseMessage(result.message);
                setError(false);
            } else {
                throw new Error('Failed to submit the form');
            }
        } catch (error) {
            setResponseMessage('Error submitting the form. Please try again.');
            setError(true);
        }
        setLoading(false);  // Hide loading spinner after submission
    };

    return (
        <div className="incident-form">
            <h2>Report an IT Incident</h2>
            <form onSubmit={handleSubmit}>
                {/* Form Fields */}
                <div>
                    <label>Name:</label>
                    <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div>
                    <label>Email:</label>
                    <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div>
                    <label>Description:</label>
                    <textarea
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        required
                    ></textarea>
                </div>

                <div>
                    <label>Category:</label>
                    <select
                        name="category"
                        value={formData.category}
                        onChange={handleChange}
                    >
                        <option value="Hardware">Hardware</option>
                        <option value="Software">Software</option>
                        <option value="Network">Network</option>
                    </select>
                </div>

                <button type="submit" disabled={loading}>Submit</button>
            </form>

            {/* Display loading spinner */}
            {loading && <div className="loading-spinner"></div>}

            {/* Display Success/Failure Messages */}
            {responseMessage && (
                <p className={error ? 'error-message' : 'success-message'}>
                    {responseMessage}
                </p>
            )}
        </div>
    );
};

export default IncidentForm;
