import React, { useState } from 'react';
import './JobForm.css';

const JobForm = ({ user }) => {
    const [formData, setFormData] = useState({
        company: '',
        role: '',
        location: '',
        job_type: '',
        h1b_sponsorship: false
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [jobs, setJobs] = useState([]);
    const [showTable, setShowTable] = useState(false);

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
        setJobs([]);
        setShowTable(false);

        try {
            const response = await fetch(`${backendUrl}/download_excel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
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
                
                // Fetch job data for table display
                await fetchJobDataForTable();
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

    const fetchJobDataForTable = async () => {
        try {
            const response = await fetch(`${backendUrl}/get_jobs_data`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success && data.jobs) {
                    setJobs(data.jobs);
                    setShowTable(true);
                }
            }
        } catch (error) {
            console.error('Error fetching job data for table:', error);
        }
    };

    return (
        <div className="job-form-container">
            <div className="form-section">
                <h2>🔍 Job Search</h2>
                <form onSubmit={handleSubmit} className="job-form">
                    <div className="form-group">
                        <label htmlFor="company">Company:</label>
                        <input
                            type="text"
                            id="company"
                            name="company"
                            value={formData.company}
                            onChange={handleInputChange}
                            placeholder="Enter company name"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="role">Role:</label>
                        <input
                            type="text"
                            id="role"
                            name="role"
                            value={formData.role}
                            onChange={handleInputChange}
                            placeholder="Enter job role"
                        />
                    </div>

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

            {/* Job Data Table */}
            {showTable && jobs.length > 0 && (
                <div className="job-table-section">
                    <JobDataTable jobs={jobs} loading={false} />
                </div>
            )}
        </div>
    );
};

// JobDataTable Component
const JobDataTable = ({ jobs, loading }) => {
    if (loading) {
        return (
            <div className="job-table-container">
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>Loading job data...</p>
                </div>
            </div>
        );
    }

    if (!jobs || jobs.length === 0) {
        return (
            <div className="job-table-container">
                <div className="no-jobs">
                    <h3>No jobs found</h3>
                    <p>Try adjusting your search criteria</p>
                </div>
            </div>
        );
    }

    return (
        <div className="job-table-container">
            <div className="table-header">
                <h3>📋 Job Search Results ({jobs.length} jobs found)</h3>
                <p className="table-subtitle">Click on job links to view full descriptions</p>
            </div>
            
            <div className="table-wrapper">
                <table className="job-table">
                    <thead>
                        <tr>
                            <th>Job Title</th>
                            <th>Company</th>
                            <th>Location</th>
                            <th>Salary</th>
                            <th>Employment Type</th>
                            <th>Interest Score</th>
                            <th>H1B Probability</th>
                            <th>Hiring Manager Contact</th>
                            <th>Job Link</th>
                        </tr>
                    </thead>
                    <tbody>
                        {jobs.map((job, index) => (
                            <tr key={index} className="job-row">
                                <td className="job-title">{job.job_title}</td>
                                <td className="company">{job.company}</td>
                                <td className="location">{job.location}</td>
                                <td className="salary">${job.salary ? job.salary.toLocaleString() : 'N/A'}</td>
                                <td className="employment-type">{job.employment_type}</td>
                                <td className="interest-score">
                                    <div className="score-bar">
                                        <div 
                                            className="score-fill" 
                                            style={{width: `${job.interest_score || 0}%`}}
                                        ></div>
                                    </div>
                                    <span className="score-text">{job.interest_score || 0}%</span>
                                </td>
                                <td className="h1b-probability">
                                    <div className="h1b-bar">
                                        <div 
                                            className="h1b-fill" 
                                            style={{width: `${job.h1b_probability || 0}%`}}
                                        ></div>
                                    </div>
                                    <span className="h1b-text">{job.h1b_probability || 0}%</span>
                                </td>
                                <td className="hiring-contact">
                                    {job.hiring_manager_contact ? (
                                        <a 
                                            href={`mailto:${job.hiring_manager_contact}`}
                                            className="contact-link"
                                            title="Send email to hiring manager"
                                        >
                                            📧 Contact
                                        </a>
                                    ) : (
                                        <span className="no-contact">N/A</span>
                                    )}
                                </td>
                                <td className="job-link">
                                    <a 
                                        href={job.job_link} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="link-button"
                                    >
                                        🔗 View Job
                                    </a>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            
            <div className="table-footer">
                <p className="data-info">
                    💡 Tip: Use the Excel download for offline viewing and sorting
                </p>
            </div>
        </div>
    );
};

export default JobForm;
