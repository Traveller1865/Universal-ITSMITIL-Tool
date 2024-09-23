import React, { useState } from 'react';

const IncidentForm = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        description: '',
        category: 'Hardware',
    });

    const [responseMessage, setResponseMessage] = useState('');

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('http://localhost:5000/api/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            const result = await response.json();
            setResponseMessage(result.message);
            console.log(result.data);
        } catch (error) {
            console.error('Error submitting the form:', error);
            setResponseMessage('Error submitting the form');
        }
    };

    return (
        <div className="incident-form">
            <h2>Report an IT Incident</h2>
            <form onSubmit={handleSubmit}>
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
                        <option value="Other">Other</option>
                    </select>
                </div>

                <button type="submit">Submit</button>
            </form>
            {responseMessage && <p>{responseMessage}</p>}
        </div>
    );
};

export default IncidentForm;
