import React, { useState } from 'react';
import '../App.css';

const JobForm = () => {
  const [loading, setLoading] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [trivia, setTrivia] = useState('');
  const [companyWeight, setCompanyWeight] = useState(50);
  const [roleWeight, setRoleWeight] = useState(50);
  const [locationWeight, setLocationWeight] = useState(50);
  const [noPreference, setNoPreference] = useState({
    company: false,
    role: false,
    location: false,
  });

  const triviaFacts = [
    "LinkedIn has over 900 million users worldwide.",
    "Google receives over 3 million job applications every year.",
    "85% of jobs are filled via networking.",
    "The tech industry is projected to grow by 11% in the next decade.",
  ];

  const handleNoPreferenceChange = (field) => {
    setNoPreference((prevState) => ({
      ...prevState,
      [field]: !prevState[field],
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setCompleted(false);

    const companies = noPreference.company
      ? [{ company: 'any', weight: 100 }]
      : [
          { company: event.target.company1.value, weight: companyWeight },
          { company: event.target.company2.value, weight: 100 - companyWeight },
        ];

    const roles = noPreference.role
      ? [{ role: 'any', weight: 100 }]
      : [
          { role: event.target.role1.value, weight: roleWeight },
          { role: event.target.role2.value, weight: 100 - roleWeight },
        ];

    const locations = noPreference.location
      ? [{ location: 'any', weight: 100 }]
      : [
          { location: event.target.location1.value, weight: locationWeight },
          { location: event.target.location2.value, weight: 100 - locationWeight },
        ];

    const params = new URLSearchParams({
      companies: JSON.stringify(companies),
      roles: JSON.stringify(roles),
      locations: JSON.stringify(locations),
      overall_company_weight: 33,
      overall_role_weight: 33,
      overall_location_weight: 34,
    });

    const backendUrl = 'https://excel-job-data3.onrender.com';
    const downloadUrl = `${backendUrl}/download_excel?${params}`;

    let triviaIndex = 0;
    const triviaInterval = setInterval(() => {
      setTrivia(triviaFacts[triviaIndex % triviaFacts.length]);
      triviaIndex++;
    }, 5000);

    try {
      const response = await fetch(downloadUrl);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = 'job_data.xlsx';
        anchor.click();
        window.URL.revokeObjectURL(url);

        setLoading(false);
        setCompleted(true);
      } else {
        throw new Error('Failed to generate the Excel file.');
      }
    } catch (error) {
      alert('An error occurred: ' + error.message);
    } finally {
      clearInterval(triviaInterval);
      setLoading(false);
    }
  };

  return (
    <div className="container">
      {loading && (
        <div id="loading">
          <div className="loader"></div>
          <p>Please give us 2 minutes to generate your jobs Excel file...</p>
          <p>{trivia}</p>
        </div>
      )}

      {!loading && !completed && (
        <form id="jobForm" onSubmit={handleSubmit}>
          <h1>Job Aggregator</h1>
          <p>Find your ideal job by prioritizing companies, roles, and locations.</p>

          {/* Target Companies */}
          <div className="form-section">
            <h3>Input Target Companies</h3>
            <label>Company 1:</label>
            <input type="text" name="company1" defaultValue="" disabled={noPreference.company} required />
            <label>Company 2:</label>
            <input type="text" name="company2" defaultValue="" disabled={noPreference.company} required />
            <label>Weight Distribution:</label>
            <input
              type="range"
              min="0"
              max="100"
              value={companyWeight}
              onChange={(e) => setCompanyWeight(Number(e.target.value))}
              disabled={noPreference.company}
            />
            <p>
              {`Company 1 Weight: ${companyWeight}% | Company 2 Weight: ${100 - companyWeight}%`}
            </p>
            <label>
              <input
                type="checkbox"
                checked={noPreference.company}
                onChange={() => handleNoPreferenceChange('company')}
              />
              No Preference
            </label>
          </div>

          {/* Target Roles */}
          <div className="form-section">
            <h3>Input Target Roles</h3>
            <label>Role 1:</label>
            <input type="text" name="role1" defaultValue="" disabled={noPreference.role} required />
            <label>Role 2:</label>
            <input type="text" name="role2" defaultValue="" disabled={noPreference.role} required />
            <label>Weight Distribution:</label>
            <input
              type="range"
              min="0"
              max="100"
              value={roleWeight}
              onChange={(e) => setRoleWeight(Number(e.target.value))}
              disabled={noPreference.role}
            />
            <p>
              {`Role 1 Weight: ${roleWeight}% | Role 2 Weight: ${100 - roleWeight}%`}
            </p>
            <label>
              <input
                type="checkbox"
                checked={noPreference.role}
                onChange={() => handleNoPreferenceChange('role')}
              />
              No Preference
            </label>
          </div>

          {/* Target Locations */}
          <div className="form-section">
            <h3>Input Target Locations(city/state)</h3>
            <label>Location 1:</label>
            <input type="text" name="location1" defaultValue="" disabled={noPreference.location} required />
            <label>Location 2:</label>
            <input type="text" name="location2" defaultValue="" disabled={noPreference.location} required />
            <label>Weight Distribution:</label>
            <input
              type="range"
              min="0"
              max="100"
              value={locationWeight}
              onChange={(e) => setLocationWeight(Number(e.target.value))}
              disabled={noPreference.location}
            />
            <p>
              {`Location 1 Weight: ${locationWeight}% | Location 2 Weight: ${100 - locationWeight}%`}
            </p>
            <label>
              <input
                type="checkbox"
                checked={noPreference.location}
                onChange={() => handleNoPreferenceChange('location')}
              />
              No Preference
            </label>
          </div>

          {/* Job Type */}
          <div className="form-section">
            <h3>Job Type</h3>
            <label>Select Job Type:</label>
            <select name="jobType" defaultValue="Full-Time">
              <option value="Full-Time">Full-Time</option>
              <option value="Part-Time">Part-Time</option>
              <option value="Internship">Internship</option>
            </select>
          </div>

          <button type="submit">Generate Excel</button>
        </form>
      )}

      {completed && (
        <div id="conclusion">
          <p>The file is ready. Please check your downloads section to find your Excel file.</p>
          <p>
            Thank you for using Job Aggregator! Would you like to{' '}
            <button
              onClick={() => window.location.reload()}
              style={{
                background: 'none',
                border: 'none',
                color: 'blue',
                textDecoration: 'underline',
                cursor: 'pointer',
              }}
            >
              try again
            </button>
            ?
          </p>
        </div>
      )}
    </div>
  );
};

export default JobForm;
