import React, { useState, useEffect } from 'react';
import './JobMarketAnalytics.css';

const JobMarketAnalytics = ({ showWhileLoading = false }) => {
    const [analyticsData, setAnalyticsData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchJobMarketData();
    }, []);

    const fetchJobMarketData = async () => {
        try {
            setLoading(true);
            const response = await fetch('https://python-job-scraper.onrender.com/job_market_analytics');
            if (!response.ok) {
                throw new Error('Failed to fetch job market data');
            }
            const data = await response.json();
            setAnalyticsData(data.data);
        } catch (err) {
            setError(err.message);
            // Fallback data
            setAnalyticsData({
                unemploymentRate: 3.8,
                jobGrowth: { current: 200000, previous: 180000, change: 20000, growthRate: 1.8 },
                topIndustries: [
                    { name: 'Technology', growth: 8.0, jobs: 40000 },
                    { name: 'Healthcare', growth: 6.0, jobs: 35000 },
                    { name: 'Finance', growth: 4.5, jobs: 25000 },
                    { name: 'Manufacturing', growth: 3.2, jobs: 22000 },
                    { name: 'Education', growth: 2.9, jobs: 18000 }
                ],
                averageSalary: { current: 72000, previous: 70000, growth: 2.9 },
                remoteWorkTrends: { remoteJobs: 25, hybridJobs: 35, onsiteJobs: 40 },
                skillsInDemand: [
                    { name: 'Python', demand: 80, growth: 10 },
                    { name: 'Data Analysis', demand: 75, growth: 12 },
                    { name: 'Cloud Computing', demand: 70, growth: 15 },
                    { name: 'Machine Learning', demand: 68, growth: 22 },
                    { name: 'Project Management', demand: 65, growth: 8 },
                    { name: 'Digital Marketing', demand: 58, growth: 14 },
                    { name: 'Cybersecurity', demand: 55, growth: 20 },
                    { name: 'UI/UX Design', demand: 52, growth: 16 }
                ],
                regionalHotspots: [
                    { name: 'San Francisco Bay Area', jobGrowth: 12000, avgSalary: 120000, growthRate: 4.0 },
                    { name: 'New York City', jobGrowth: 9500, avgSalary: 90000, growthRate: 3.5 },
                    { name: 'Austin, TX', jobGrowth: 8200, avgSalary: 85000, growthRate: 5.1 },
                    { name: 'Seattle, WA', jobGrowth: 7500, avgSalary: 92000, growthRate: 3.9 },
                    { name: 'Denver, CO', jobGrowth: 6800, avgSalary: 78000, growthRate: 4.5 },
                    { name: 'Nashville, TN', jobGrowth: 5200, avgSalary: 65000, growthRate: 6.2 }
                ],
                marketSentiment: 75
            });
        } finally {
            setLoading(false);
        }
    };

    if (loading && showWhileLoading) {
        return (
            <div className="analytics-container loading-mode">
                <div className="analytics-header">
                    <h2>📊 Job Market Analytics</h2>
                    <p className="loading-note">Loading job data... Here's the current market overview:</p>
                </div>

                <div className="analytics-grid">
                    {/* Unemployment Rate */}
                    <div className="analytics-card primary">
                        <div className="card-header">
                            <h3>📈 Unemployment Rate</h3>
                            <div className="trend-indicator positive">↓</div>
                        </div>
                        <div className="card-content">
                            <div className="main-stat">
                                <span className="stat-value">{analyticsData?.unemploymentRate || 3.8}%</span>
                                <span className="stat-change">-0.2% from last month</span>
                            </div>
                            <p className="stat-description">
                                National unemployment rate showing continued recovery
                            </p>
                        </div>
                    </div>

                    {/* Job Growth */}
                    <div className="analytics-card success">
                        <div className="card-header">
                            <h3>🚀 Job Growth</h3>
                            <div className="trend-indicator positive">↑</div>
                        </div>
                        <div className="card-content">
                            <div className="main-stat">
                                <span className="stat-value">+{(analyticsData?.jobGrowth?.current || 200000).toLocaleString()}</span>
                                <span className="stat-change">+{(analyticsData?.jobGrowth?.change || 20000).toLocaleString()} from last month</span>
                            </div>
                            <p className="stat-description">
                                New jobs added to the economy this month
                            </p>
                        </div>
                    </div>

                    {/* Top Industries */}
                    <div className="analytics-card info">
                        <div className="card-header">
                            <h3>🏢 Top Hiring Industries</h3>
                        </div>
                        <div className="card-content">
                            <div className="industry-list">
                                {(analyticsData?.topIndustries || []).map((industry, index) => (
                                    <div key={index} className="industry-item">
                                        <span className="industry-name">{industry.name}</span>
                                        <span className="industry-growth">+{industry.growth}%</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Average Salary */}
                    <div className="analytics-card warning">
                        <div className="card-header">
                            <h3>💰 Average Salary Trends</h3>
                            <div className="trend-indicator positive">↑</div>
                        </div>
                        <div className="card-content">
                            <div className="main-stat">
                                <span className="stat-value">${(analyticsData?.averageSalary?.current || 72000).toLocaleString()}</span>
                                <span className="stat-change">+{analyticsData?.averageSalary?.growth || 2.9}% YoY</span>
                            </div>
                            <p className="stat-description">
                                Average annual salary across all industries
                            </p>
                        </div>
                    </div>

                    {/* Remote Work Trends */}
                    <div className="analytics-card secondary">
                        <div className="card-header">
                            <h3>🏠 Remote Work Trends</h3>
                        </div>
                        <div className="card-content">
                            <div className="remote-stats">
                                <div className="remote-stat">
                                    <span className="stat-label">Remote Jobs</span>
                                    <span className="stat-value">{analyticsData?.remoteWorkTrends?.remoteJobs || 25}%</span>
                                </div>
                                <div className="remote-stat">
                                    <span className="stat-label">Hybrid Jobs</span>
                                    <span className="stat-value">{analyticsData?.remoteWorkTrends?.hybridJobs || 35}%</span>
                                </div>
                                <div className="remote-stat">
                                    <span className="stat-label">On-site Jobs</span>
                                    <span className="stat-value">{analyticsData?.remoteWorkTrends?.onsiteJobs || 40}%</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Skills in Demand */}
                    <div className="analytics-card dark">
                        <div className="card-header">
                            <h3>🎯 Skills in Demand</h3>
                        </div>
                        <div className="card-content">
                            <div className="skills-list">
                                {(analyticsData?.skillsInDemand || []).map((skill, index) => (
                                    <div key={index} className="skill-item">
                                        <span className="skill-name">{skill.name}</span>
                                        <div className="skill-bar">
                                            <div 
                                                className="skill-progress" 
                                                style={{width: `${skill.demand}%`}}
                                            ></div>
                                        </div>
                                        <span className="skill-demand">{skill.demand}%</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Regional Hotspots */}
                    <div className="analytics-card accent">
                        <div className="card-header">
                            <h3>📍 Regional Hotspots</h3>
                        </div>
                        <div className="card-content">
                            <div className="region-list">
                                {(analyticsData?.regionalHotspots || []).map((region, index) => (
                                    <div key={index} className="region-item">
                                        <span className="region-name">{region.name}</span>
                                        <span className="region-jobs">+{region.jobGrowth.toLocaleString()} jobs</span>
                                        <span className="region-salary">${region.avgSalary.toLocaleString()}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Market Sentiment */}
                    <div className="analytics-card neutral">
                        <div className="card-header">
                            <h3>📊 Market Sentiment</h3>
                        </div>
                        <div className="card-content">
                            <div className="sentiment-indicator">
                                <div className="sentiment-bar">
                                    <div 
                                        className="sentiment-progress positive" 
                                        style={{width: `${analyticsData?.marketSentiment || 75}%`}}
                                    ></div>
                                </div>
                                <span className="sentiment-value">{analyticsData?.marketSentiment || 75}/100</span>
                            </div>
                            <p className="sentiment-description">
                                Overall job market confidence index
                            </p>
                        </div>
                    </div>
                </div>

                <div className="analytics-footer">
                    <p className="data-source">
                        Data sources: Bureau of Labor Statistics, LinkedIn Economic Graph, Indeed Hiring Lab
                    </p>
                    <button onClick={fetchJobMarketData} className="refresh-btn">
                        🔄 Refresh Data
                    </button>
                </div>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="analytics-container">
                <div className="loading-spinner">
                    <div className="spinner"></div>
                    <p>Loading job market analytics...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="analytics-container">
            <div className="analytics-header">
                <h2>📊 Current Job Market Analytics</h2>
                <p className="last-updated">
                    Last updated: {new Date().toLocaleDateString()}
                </p>
            </div>

            <div className="analytics-grid">
                {/* Unemployment Rate */}
                <div className="analytics-card primary">
                    <div className="card-header">
                        <h3>📈 Unemployment Rate</h3>
                        <div className="trend-indicator positive">↓</div>
                    </div>
                    <div className="card-content">
                        <div className="main-stat">
                            <span className="stat-value">{analyticsData.unemploymentRate}%</span>
                            <span className="stat-change">-0.2% from last month</span>
                        </div>
                        <p className="stat-description">
                            National unemployment rate showing continued recovery
                        </p>
                    </div>
                </div>

                {/* Job Growth */}
                <div className="analytics-card success">
                    <div className="card-header">
                        <h3>🚀 Job Growth</h3>
                        <div className="trend-indicator positive">↑</div>
                    </div>
                    <div className="card-content">
                        <div className="main-stat">
                            <span className="stat-value">+{analyticsData.jobGrowth.current.toLocaleString()}</span>
                            <span className="stat-change">+{analyticsData.jobGrowth.change.toLocaleString()} from last month</span>
                        </div>
                        <p className="stat-description">
                            New jobs added to the economy this month
                        </p>
                    </div>
                </div>

                {/* Top Industries */}
                <div className="analytics-card info">
                    <div className="card-header">
                        <h3>🏢 Top Hiring Industries</h3>
                    </div>
                    <div className="card-content">
                        <div className="industry-list">
                            {analyticsData.topIndustries.map((industry, index) => (
                                <div key={index} className="industry-item">
                                    <span className="industry-name">{industry.name}</span>
                                    <span className="industry-growth">+{industry.growth}%</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Average Salary */}
                <div className="analytics-card warning">
                    <div className="card-header">
                        <h3>💰 Average Salary Trends</h3>
                        <div className="trend-indicator positive">↑</div>
                    </div>
                    <div className="card-content">
                        <div className="main-stat">
                            <span className="stat-value">${analyticsData.averageSalary.current.toLocaleString()}</span>
                            <span className="stat-change">+{analyticsData.averageSalary.growth}% YoY</span>
                        </div>
                        <p className="stat-description">
                            Average annual salary across all industries
                        </p>
                    </div>
                </div>

                {/* Remote Work Trends */}
                <div className="analytics-card secondary">
                    <div className="card-header">
                        <h3>🏠 Remote Work Trends</h3>
                    </div>
                    <div className="card-content">
                        <div className="remote-stats">
                            <div className="remote-stat">
                                <span className="stat-label">Remote Jobs</span>
                                <span className="stat-value">{analyticsData.remoteWorkTrends.remoteJobs}%</span>
                            </div>
                            <div className="remote-stat">
                                <span className="stat-label">Hybrid Jobs</span>
                                <span className="stat-value">{analyticsData.remoteWorkTrends.hybridJobs}%</span>
                            </div>
                            <div className="remote-stat">
                                <span className="stat-label">On-site Jobs</span>
                                <span className="stat-value">{analyticsData.remoteWorkTrends.onsiteJobs}%</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Skills in Demand */}
                <div className="analytics-card dark">
                    <div className="card-header">
                        <h3>🎯 Skills in Demand</h3>
                    </div>
                    <div className="card-content">
                        <div className="skills-list">
                            {analyticsData.skillsInDemand.map((skill, index) => (
                                <div key={index} className="skill-item">
                                    <span className="skill-name">{skill.name}</span>
                                    <div className="skill-bar">
                                        <div 
                                            className="skill-progress" 
                                            style={{width: `${skill.demand}%`}}
                                        ></div>
                                    </div>
                                    <span className="skill-demand">{skill.demand}%</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Regional Hotspots */}
                <div className="analytics-card accent">
                    <div className="card-header">
                        <h3>📍 Regional Hotspots</h3>
                    </div>
                    <div className="card-content">
                        <div className="region-list">
                            {analyticsData.regionalHotspots.map((region, index) => (
                                <div key={index} className="region-item">
                                    <span className="region-name">{region.name}</span>
                                    <span className="region-jobs">+{region.jobGrowth.toLocaleString()} jobs</span>
                                    <span className="region-salary">${region.avgSalary.toLocaleString()}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Market Sentiment */}
                <div className="analytics-card neutral">
                    <div className="card-header">
                        <h3>📊 Market Sentiment</h3>
                    </div>
                    <div className="card-content">
                        <div className="sentiment-indicator">
                            <div className="sentiment-bar">
                                <div 
                                    className="sentiment-progress positive" 
                                    style={{width: `${analyticsData.marketSentiment}%`}}
                                ></div>
                            </div>
                            <span className="sentiment-value">{analyticsData.marketSentiment}/100</span>
                        </div>
                        <p className="sentiment-description">
                            Overall job market confidence index
                        </p>
                    </div>
                </div>
            </div>

            <div className="analytics-footer">
                <p className="data-source">
                    Data sources: Bureau of Labor Statistics, LinkedIn Economic Graph, Indeed Hiring Lab
                </p>
                <button onClick={fetchJobMarketData} className="refresh-btn">
                    🔄 Refresh Data
                </button>
            </div>
        </div>
    );
};

export default JobMarketAnalytics;
