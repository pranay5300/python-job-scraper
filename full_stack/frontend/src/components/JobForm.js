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
    "Amazon is the second-largest employer in the United States.",
    "Remote jobs have increased by over 91% in the past decade.",
    "Data Scientist has been named the sexiest job of the 21st century.",
    "Apple was founded in a garage in Cupertino, California.",
    "Facebook changed its name to Meta in 2021.",
    "The first-ever email was sent in 1971.",
    "Python is the most in-demand programming language.",
    "Microsoft has over 220,000 employees globally.",
    "The first website was published in 1991 by Tim Berners-Lee.",
    "Over 70% of jobs are never posted publicly.",
    "The world's largest employer is Walmart with over 2 million employees.",
    "80% of resumes are rejected in less than 11 seconds.",
    "Tesla’s Gigafactories are among the largest buildings in the world.",
    "The average salary for a Software Engineer in the US is $110,000.",
    "Cybersecurity jobs are expected to grow by 31% by 2029.",
    "Netflix employees enjoy unlimited vacation days.",
    "The first job board website went live in 1994.",
    "Over 50% of the global workforce now works remotely at least once a week.",
    "The tech industry has one of the lowest unemployment rates.",
    "Google employees are called Googlers.",
    "IBM was founded over a century ago in 1911.",
    "SpaceX was the first private company to send astronauts to space.",
    "The average time to fill a job vacancy is 42 days.",
    "Amazon Web Services (AWS) powers over 30% of the internet.",
    "The first LinkedIn post was made in 2003.",
    "There are over 7 million job openings in the US at any given time.",
    "Coding bootcamps have a job placement rate of over 80%.",
    "The highest-paying job in the US is Anesthesiologist.",
    "The average cost of a bad hire is up to 30% of their annual salary.",
    "YouTube is the second most visited website in the world.",
    "The first Apple computer was sold for $666.66.",
    "Over 1 billion people use Microsoft Office globally.",
    "There are over 700,000 tech startups worldwide.",
    "Adobe Photoshop was first released in 1988.",
    "GitHub has over 100 million repositories.",
    "Google was initially called BackRub.",
    "The first smartphone was released in 1992 by IBM.",
    "The most in-demand soft skill is communication.",
    "The fastest-growing job in the US is Wind Turbine Technician.",
    "The tech sector accounts for 10% of the US GDP.",
    "Slack was originally a gaming company.",
    "Twitter was founded in 2006 and was originally called Twttr.",
    "Over 2 million cybersecurity jobs will be unfilled by 2025."
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

    const backendUrl = 'https://python-job-scraper.onrender.com';
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
          <h1>to jobdatacamp</h1>
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
