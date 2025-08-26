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
  const [includeH1B, setIncludeH1B] = useState(false);

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
      include_h1b: includeH1B.toString(),
      job_type: event.target.jobType.value,
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
    <div className="main-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Find Your Dream Job</h1>
          <p className="hero-subtitle">
            Discover opportunities that match your preferences with our intelligent job matching system
          </p>
        </div>
      </section>

      {loading && (
        <div className="loading-overlay">
          <div className="loading-card">
            <div className="loader"></div>
            <h3>Searching for Your Perfect Jobs</h3>
            <p>Please give us 2 minutes to generate your personalized job recommendations...</p>
            <div className="trivia-section">
              <p className="trivia-label">💡 Did you know?</p>
              <p className="trivia-text">{trivia}</p>
            </div>
          </div>
        </div>
      )}

      {!loading && !completed && (
        <section className="search-section">
          <div className="search-container">
            <div className="search-header">
              <h2>Customize Your Job Search</h2>
              <p>Tell us about your preferences and we'll find the best opportunities for you</p>
            </div>
            
            <form className="job-search-form" onSubmit={handleSubmit}>

              {/* Target Companies */}
              <div className="form-card">
                <div className="card-header">
                  <span className="card-icon">🏢</span>
                  <h3>Target Companies</h3>
                </div>
                <div className="card-content">
                  <div className="input-group">
                    <label className="input-label">Preferred Company</label>
                    <input 
                      type="text" 
                      name="company1" 
                      className="form-input"
                      placeholder="e.g., Google, Microsoft, Apple"
                      disabled={noPreference.company} 
                      required 
                    />
                  </div>
                  <div className="input-group">
                    <label className="input-label">Alternative Company</label>
                    <input 
                      type="text" 
                      name="company2" 
                      className="form-input"
                      placeholder="e.g., Amazon, Meta, Netflix"
                      disabled={noPreference.company} 
                      required 
                    />
                  </div>
                  <div className="slider-group">
                    <label className="input-label">Preference Distribution</label>
                    <div className="slider-container">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={companyWeight}
                        className="preference-slider"
                        onChange={(e) => setCompanyWeight(Number(e.target.value))}
                        disabled={noPreference.company}
                      />
                      <div className="slider-labels">
                        <span>Primary: {companyWeight}%</span>
                        <span>Alternative: {100 - companyWeight}%</span>
                      </div>
                    </div>
                  </div>
                  <div className="checkbox-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={noPreference.company}
                        onChange={() => handleNoPreferenceChange('company')}
                      />
                      <span className="checkmark"></span>
                      Open to any company
                    </label>
                  </div>
                </div>
              </div>

              {/* Target Roles */}
              <div className="form-card">
                <div className="card-header">
                  <span className="card-icon">💻</span>
                  <h3>Target Roles</h3>
                </div>
                <div className="card-content">
                  <div className="input-group">
                    <label className="input-label">Preferred Role</label>
                    <input 
                      type="text" 
                      name="role1" 
                      className="form-input"
                      placeholder="e.g., Software Engineer, Data Scientist"
                      disabled={noPreference.role} 
                      required 
                    />
                  </div>
                  <div className="input-group">
                    <label className="input-label">Alternative Role</label>
                    <input 
                      type="text" 
                      name="role2" 
                      className="form-input"
                      placeholder="e.g., Product Manager, UX Designer"
                      disabled={noPreference.role} 
                      required 
                    />
                  </div>
                  <div className="slider-group">
                    <label className="input-label">Preference Distribution</label>
                    <div className="slider-container">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={roleWeight}
                        className="preference-slider"
                        onChange={(e) => setRoleWeight(Number(e.target.value))}
                        disabled={noPreference.role}
                      />
                      <div className="slider-labels">
                        <span>Primary: {roleWeight}%</span>
                        <span>Alternative: {100 - roleWeight}%</span>
                      </div>
                    </div>
                  </div>
                  <div className="checkbox-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={noPreference.role}
                        onChange={() => handleNoPreferenceChange('role')}
                      />
                      <span className="checkmark"></span>
                      Open to any role
                    </label>
                  </div>
                </div>
              </div>

              {/* Target Locations */}
              <div className="form-card">
                <div className="card-header">
                  <span className="card-icon">📍</span>
                  <h3>Target Locations</h3>
                </div>
                <div className="card-content">
                  <div className="input-group">
                    <label className="input-label">Preferred Location</label>
                    <input 
                      type="text" 
                      name="location1" 
                      className="form-input"
                      placeholder="e.g., San Francisco, CA"
                      disabled={noPreference.location} 
                      required 
                    />
                  </div>
                  <div className="input-group">
                    <label className="input-label">Alternative Location</label>
                    <input 
                      type="text" 
                      name="location2" 
                      className="form-input"
                      placeholder="e.g., New York, NY"
                      disabled={noPreference.location} 
                      required 
                    />
                  </div>
                  <div className="slider-group">
                    <label className="input-label">Preference Distribution</label>
                    <div className="slider-container">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={locationWeight}
                        className="preference-slider"
                        onChange={(e) => setLocationWeight(Number(e.target.value))}
                        disabled={noPreference.location}
                      />
                      <div className="slider-labels">
                        <span>Primary: {locationWeight}%</span>
                        <span>Alternative: {100 - locationWeight}%</span>
                      </div>
                    </div>
                  </div>
                  <div className="checkbox-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={noPreference.location}
                        onChange={() => handleNoPreferenceChange('location')}
                      />
                      <span className="checkmark"></span>
                      Open to any location
                    </label>
                  </div>
                </div>
              </div>

              {/* Job Type */}
              <div className="form-card">
                <div className="card-header">
                  <span className="card-icon">⏰</span>
                  <h3>Job Type</h3>
                </div>
                <div className="card-content">
                  <div className="input-group">
                    <label className="input-label">Employment Type</label>
                    <select name="jobType" className="form-select" defaultValue="Full-Time">
                      <option value="Full-Time">Full-Time</option>
                      <option value="Part-Time">Part-Time</option>
                      <option value="Internship">Internship</option>
                      <option value="Contract">Contract</option>
                      <option value="Remote">Remote</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* H1B Visa Sponsorship */}
              <div className="form-card">
                <div className="card-header">
                  <span className="card-icon">🛂</span>
                  <h3>Visa Sponsorship</h3>
                </div>
                <div className="card-content">
                  <div className="checkbox-group">
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={includeH1B}
                        onChange={(e) => setIncludeH1B(e.target.checked)}
                      />
                      <span className="checkmark"></span>
                      Include H1B sponsorship prediction
                    </label>
                    <p className="checkbox-description">
                      When enabled, an additional column will show the probability (%) that each company sponsors H1B visas for the specific role.
                    </p>
                  </div>
                </div>
              </div>

              <div className="submit-section">
                <button type="submit" className="submit-btn">
                  <span className="btn-icon">🔍</span>
                  Find My Perfect Jobs
                </button>
                <p className="submit-note">
                  We'll search through thousands of job listings to find your perfect match
                </p>
              </div>
            </form>
          </div>
        </section>
      )}

      {completed && (
        <section className="success-section">
          <div className="success-card">
            <div className="success-icon">✅</div>
            <h2>Your Job Search Results Are Ready!</h2>
            <p className="success-message">
              We've found personalized job recommendations based on your preferences. 
              Please check your downloads folder for your Excel file.
            </p>
            <div className="success-actions">
              <button
                onClick={() => window.location.reload()}
                className="restart-btn"
              >
                🔄 Search Again
              </button>
            </div>
            <p className="thank-you">
              Thank you for using JobDataCamp! We hope you find your dream job.
            </p>
          </div>
        </section>
      )}
    </div>
  );
};

export default JobForm;
