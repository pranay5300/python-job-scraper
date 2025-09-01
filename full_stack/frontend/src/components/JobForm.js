import React, { useState } from 'react';
import './JobForm.css';

const JobForm = ({ user }) => {
    const [formData, setFormData] = useState({
        company1: '',
        company1_weight: 50,
        company2: '',
        company2_weight: 50,
        role1: '',
        role1_weight: 50,
        role2: '',
        role2_weight: 50,
        location: '',
        job_type: '',
        h1b_sponsorship: false
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    const backendUrl = 'https://python-job-scraper.onrender.com';

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');

        // Prepare data for backend (combine companies and roles)
        const backendData = {
            company: `${formData.company1} ${formData.company2}`.trim(),
            role: `${formData.role1} ${formData.role2}`.trim(),
            location: formData.location,
            job_type: formData.job_type,
            h1b_sponsorship: formData.h1b_sponsorship,
            // Include weightages for backend processing
            company1: formData.company1,
            company1_weight: formData.company1_weight,
            company2: formData.company2,
            company2_weight: formData.company2_weight,
            role1: formData.role1,
            role1_weight: formData.role1_weight,
            role2: formData.role2,
            role2_weight: formData.role2_weight
        };

        try {
            const response = await fetch(`${backendUrl}/download_excel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(backendData)
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'job_data.xlsx';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                setMessage('✅ Excel file downloaded successfully!');
            } else {
                const errorData = await response.json();
                setMessage(`❌ Error: ${errorData.error || 'Failed to download Excel file'}`);
            }
        } catch (error) {
            setMessage(`❌ Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="job-form-container">
            <div className="form-section">
                <h2>🔍 Job Search</h2>
                <form onSubmit={handleSubmit} className="job-form">
                    {/* Company Section */}
                    <div className="form-section-group">
                        <h3>🏢 Companies</h3>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="company1">Company 1:</label>
                                <input
                                    type="text"
                                    id="company1"
                                    name="company1"
                                    value={formData.company1}
                                    onChange={handleInputChange}
                                    placeholder="Enter first company name"
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="company1_weight">Weight (%):</label>
                                <input
                                    type="number"
                                    id="company1_weight"
                                    name="company1_weight"
                                    value={formData.company1_weight}
                                    onChange={handleInputChange}
                                    min="0"
                                    max="100"
                                />
                            </div>
                        </div>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="company2">Company 2:</label>
                                <input
                                    type="text"
                                    id="company2"
                                    name="company2"
                                    value={formData.company2}
                                    onChange={handleInputChange}
                                    placeholder="Enter second company name"
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="company2_weight">Weight (%):</label>
                                <input
                                    type="number"
                                    id="company2_weight"
                                    name="company2_weight"
                                    value={formData.company2_weight}
                                    onChange={handleInputChange}
                                    min="0"
                                    max="100"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Role Section */}
                    <div className="form-section-group">
                        <h3>💼 Roles</h3>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="role1">Role 1:</label>
                                <input
                                    type="text"
                                    id="role1"
                                    name="role1"
                                    value={formData.role1}
                                    onChange={handleInputChange}
                                    placeholder="Enter first role"
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="role1_weight">Weight (%):</label>
                                <input
                                    type="number"
                                    id="role1_weight"
                                    name="role1_weight"
                                    value={formData.role1_weight}
                                    onChange={handleInputChange}
                                    min="0"
                                    max="100"
                                />
                            </div>
                        </div>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="role2">Role 2:</label>
                                <input
                                    type="text"
                                    id="role2"
                                    name="role2"
                                    value={formData.role2}
                                    onChange={handleInputChange}
                                    placeholder="Enter second role"
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="role2_weight">Weight (%):</label>
                                <input
                                    type="number"
                                    id="role2_weight"
                                    name="role2_weight"
                                    value={formData.role2_weight}
                                    onChange={handleInputChange}
                                    min="0"
                                    max="100"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Location and Job Type */}
                    <div className="form-section-group">
                        <h3>📍 Location & Type</h3>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="location">Location:</label>
                                <input
                                    type="text"
                                    id="location"
                                    name="location"
                                    value={formData.location}
                                    onChange={handleInputChange}
                                    placeholder="Enter location or 'any'"
                                />
                            </div>
                            <div className="form-group">
                                <label htmlFor="job_type">Employment Type:</label>
                                <select
                                    id="job_type"
                                    name="job_type"
                                    value={formData.job_type}
                                    onChange={handleInputChange}
                                >
                                    <option value="">Any Type</option>
                                    <option value="full-time">Full-time</option>
                                    <option value="part-time">Part-time</option>
                                    <option value="contract">Contract</option>
                                    <option value="internship">Internship</option>
                                    <option value="remote">Remote</option>
                                    <option value="hybrid">Hybrid</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* H1B Sponsorship */}
                    <div className="form-group checkbox-group">
                        <label>
                            <input
                                type="checkbox"
                                name="h1b_sponsorship"
                                checked={formData.h1b_sponsorship}
                                onChange={handleInputChange}
                            />
                            H1B Sponsorship Required
                        </label>
                    </div>

                    <button type="submit" disabled={loading} className="submit-btn">
                        {loading ? '🔍 Searching Jobs...' : '📥 Download Excel'}
                    </button>
                </form>

                {message && (
                    <div className={`message ${message.includes('✅') ? 'success' : 'error'}`}>
                        {message}
                    </div>
                )}
            </div>
        </div>
    );
};

export default JobForm;
