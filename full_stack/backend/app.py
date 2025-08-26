import asyncio
import os
import sys
import time
import hashlib
import io
import sqlite3
import json
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import numpy as np
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure CORS for development and production
CORS(app, resources={
    r"/api/*": {"origins": "*"},
    r"/download_excel": {"origins": "*"},
    r"/": {"origins": "*"},
    r"/health": {"origins": "*"},
    r"/stats": {"origins": "*"},
    r"/test_h1b": {"origins": "*"}
})

class FastJobDatabase:
    """Fast in-memory job database with SQLite persistence."""
    
    def __init__(self):
        self.db_path = 'fast_jobs.db'
        self.cache = {}
        self.h1b_cache = {}
        self.initialized = False
        
    def initialize(self):
        """Initialize database with sample data."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create jobs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY,
                    job_title TEXT,
                    company_name TEXT,
                    location TEXT,
                    job_link TEXT,
                    work_type TEXT,
                    salary TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_company ON jobs(company_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_title ON jobs(job_title)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_location ON jobs(location)')
            
            # Check if we need to populate
            cursor.execute('SELECT COUNT(*) FROM jobs')
            count = cursor.fetchone()[0]
            
            if count == 0:
                self._populate_sample_data(cursor)
            
            conn.commit()
            conn.close()
            self.initialized = True
            logger.info("Fast job database initialized")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def _populate_sample_data(self, cursor):
        """Populate database with realistic job data."""
        companies = [
            'Google', 'Microsoft', 'Amazon', 'Apple', 'Meta', 'Netflix', 'Tesla',
            'NVIDIA', 'Intel', 'Cisco', 'Oracle', 'IBM', 'Salesforce', 'Adobe',
            'Uber', 'Airbnb', 'Spotify', 'LinkedIn', 'Twitter', 'Snap',
            'Goldman Sachs', 'JPMorgan Chase', 'Bank of America', 'Wells Fargo',
            'Accenture', 'Deloitte', 'McKinsey & Company', 'BCG', 'Bain & Company'
        ]
        
        job_titles = [
            'Software Engineer', 'Senior Software Engineer', 'Principal Engineer',
            'Data Scientist', 'Machine Learning Engineer', 'AI Engineer',
            'Backend Engineer', 'Frontend Engineer', 'Full Stack Engineer',
            'DevOps Engineer', 'Cloud Engineer', 'Security Engineer',
            'Product Manager', 'Technical Program Manager', 'Engineering Manager',
            'Solutions Architect', 'Data Engineer', 'Platform Engineer',
            'Site Reliability Engineer', 'Mobile Engineer', 'QA Engineer'
        ]
        
        locations = [
            'San Francisco, CA', 'New York, NY', 'Seattle, WA', 'Austin, TX',
            'Boston, MA', 'Chicago, IL', 'Los Angeles, CA', 'Denver, CO',
            'Atlanta, GA', 'Raleigh, NC', 'Remote', 'Mountain View, CA',
            'Palo Alto, CA', 'Redmond, WA', 'Cambridge, MA'
        ]
        
        work_types = ['Full-time', 'Part-time', 'Contract', 'Remote', 'Hybrid']
        
        salaries = [
            '$80,000 - $120,000', '$120,000 - $160,000', '$160,000 - $200,000',
            '$200,000 - $250,000', '$250,000 - $300,000', '$300,000+',
            'Competitive', 'N/A'
        ]
        
        sources = ['LinkedIn', 'Indeed', 'Glassdoor']
        
        jobs_data = []
        for i in range(1000):  # Generate 1000 sample jobs
            company = random.choice(companies)
            title = random.choice(job_titles)
            location = random.choice(locations)
            work_type = random.choice(work_types)
            salary = random.choice(salaries)
            source = random.choice(sources)
            
            job_link = f'https://{source.lower()}.com/jobs/{company.lower().replace(" ", "-")}-{title.lower().replace(" ", "-")}-{i}'
            
            jobs_data.append((title, company, location, job_link, work_type, salary, source))
        
        cursor.executemany('''
            INSERT INTO jobs (job_title, company_name, location, job_link, work_type, salary, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', jobs_data)
        
        logger.info(f"Populated database with {len(jobs_data)} sample jobs")
    
    def search_jobs(self, companies, roles, locations, job_type='Full-time', limit=500):
        """Fast job search with filtering."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query
            where_conditions = []
            params = []
            
            # Company filter 
            if companies and not (len(companies) == 1 and companies[0].get('company') == 'any'):
                company_conditions = []
                for company in companies:
                    if company.get('company') and company['company'] != 'any':
                        # Simple case-insensitive matching
                        company_conditions.append('LOWER(company_name) LIKE ?')
                        params.append(f"%{company['company'].lower()}%")
                if company_conditions:
                    where_conditions.append(f"({' OR '.join(company_conditions)})")
            
            # Role filter
            if roles and not (len(roles) == 1 and roles[0].get('role') == 'any'):
                role_conditions = []
                for role in roles:
                    if role.get('role') and role['role'] != 'any':
                        # Simple case-insensitive matching
                        role_conditions.append('LOWER(job_title) LIKE ?')
                        params.append(f"%{role['role'].lower()}%")
                if role_conditions:
                    where_conditions.append(f"({' OR '.join(role_conditions)})")
            
            # Location filter
            if locations and not (len(locations) == 1 and locations[0].get('location') == 'any'):
                location_conditions = []
                for location in locations:
                    if location.get('location') and location['location'] != 'any':
                        # Simple case-insensitive matching
                        location_conditions.append('LOWER(location) LIKE ?')
                        params.append(f"%{location['location'].lower()}%")
                if location_conditions:
                    where_conditions.append(f"({' OR '.join(location_conditions)})")
            
            # Job type filter
            if job_type and job_type.lower() != 'any':
                where_conditions.append('work_type LIKE ?')
                params.append(f"%{job_type}%")
            
            # Build final query
            query = '''
                SELECT job_title, company_name, location, job_link, work_type, salary, source
                FROM jobs
            '''
            
            if where_conditions:
                query += ' WHERE ' + ' AND '.join(where_conditions)
            
            query += f' ORDER BY created_at DESC LIMIT {limit}'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to dict format
            jobs = []
            for row in rows:
                jobs.append({
                    'job_title': row[0],
                    'company_name': row[1],
                    'location': row[2],
                    'job_link': row[3],
                    'work_type': row[4],
                    'salary': row[5],
                    'source': row[6]
                })
            
            return jobs
            
        except Exception as e:
            logger.error(f"Job search error: {e}")
            return []

class FastH1BPredictor:
    """Fast H1B sponsorship predictor using rule-based approach."""
    
    def __init__(self):
        # Companies known to sponsor H1B visas with probabilities
        self.h1b_sponsors = {
            'google': 0.95, 'microsoft': 0.94, 'amazon': 0.92, 'apple': 0.90,
            'meta': 0.89, 'facebook': 0.89, 'netflix': 0.87, 'tesla': 0.85,
            'nvidia': 0.88, 'intel': 0.86, 'cisco': 0.84, 'oracle': 0.83,
            'ibm': 0.82, 'salesforce': 0.85, 'adobe': 0.83, 'uber': 0.80,
            'airbnb': 0.78, 'spotify': 0.76, 'linkedin': 0.82, 'twitter': 0.75,
            'snap': 0.73, 'palantir': 0.81, 'databricks': 0.79, 'snowflake': 0.77,
            'goldman sachs': 0.75, 'jpmorgan': 0.73, 'bank of america': 0.70,
            'wells fargo': 0.68, 'accenture': 0.78, 'deloitte': 0.76,
            'mckinsey': 0.74, 'bcg': 0.73, 'bain': 0.72,
            'qualcomm': 0.84, 'broadcom': 0.82, 'amd': 0.80, 'micron': 0.78
        }
        
        # Tech roles that are more likely to be sponsored
        self.tech_roles = [
            'software engineer', 'data scientist', 'machine learning', 'ai engineer',
            'backend engineer', 'frontend engineer', 'full stack', 'devops',
            'cloud engineer', 'security engineer', 'platform engineer',
            'site reliability', 'data engineer', 'solutions architect'
        ]
    
    def predict_probability(self, company, role):
        """Predict H1B sponsorship probability."""
        company_lower = company.lower()
        role_lower = role.lower()
        
        # Base probability from company
        base_prob = 0.3  # Default probability
        
        for known_company, prob in self.h1b_sponsors.items():
            if known_company in company_lower:
                base_prob = prob
                break
        
        # Adjust based on role
        is_tech_role = any(tech_role in role_lower for tech_role in self.tech_roles)
        
        if is_tech_role:
            # Boost for tech roles
            final_prob = min(base_prob * 1.1, 1.0)
        elif any(word in role_lower for word in ['manager', 'director', 'analyst']):
            # Slight boost for management/analytical roles
            final_prob = min(base_prob * 1.05, 1.0)
        else:
            # Reduce for non-tech roles
            final_prob = base_prob * 0.7
        
        return round(final_prob * 100, 1)  # Return as percentage

class FastJobMatcher:
    """Fast job matching and scoring."""
    
    def calculate_job_scores(self, jobs, companies, roles, locations, weights):
        """Calculate match scores for jobs."""
        for job in jobs:
            company_score = 0
            role_score = 0
            location_score = 0
            
            # Company score
            for company in companies:
                if company.get('company', '').lower() != 'any':
                    if company['company'].lower() in job['company_name'].lower():
                        company_score = max(company_score, float(company['weight']) / 100)
            
            # Role score
            for role in roles:
                if role.get('role', '').lower() != 'any':
                    if role['role'].lower() in job['job_title'].lower():
                        role_score = max(role_score, float(role['weight']) / 100)
            
            # Location score
            for location in locations:
                if location.get('location', '').lower() != 'any':
                    if location['location'].lower() in job['location'].lower():
                        location_score = max(location_score, float(location['weight']) / 100)
            
            # Calculate final score
            final_score = (
                company_score * weights['company_weight'] +
                role_score * weights['role_weight'] +
                location_score * weights['location_weight']
            )
            
            job['match_score'] = round(final_score * 100, 1)
        
        # Sort by score
        return sorted(jobs, key=lambda x: x['match_score'], reverse=True)

# Initialize components
job_db = FastJobDatabase()
h1b_predictor = FastH1BPredictor()
job_matcher = FastJobMatcher()

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information."""
    return jsonify({
        "service": "JobDataCamp API",
        "version": "1.0.0",
        "status": "healthy",
        "description": "TAMU Job Search API with H1B Predictions",
        "endpoints": {
            "health": "/health",
            "stats": "/stats", 
            "test_h1b": "/test_h1b",
            "download_excel": "/download_excel",
            "ip_info": "/ip_info",
            "debug_companies": "/debug_companies"
        },
        "production_url": "https://python-job-scraper.onrender.com",
        "documentation": "See DEBUG_GUIDE.md for complete API usage",
        "frontend_compatible": True,
        "cors_enabled": True
    })

@app.route('/download_excel', methods=['GET'])
def download_excel():
    """Ultra-fast Excel generation endpoint."""
    start_time = time.time()
    
    try:
        # Parse parameters
        companies = json.loads(request.args.get("companies", "[]"))
        roles = json.loads(request.args.get("roles", "[]"))
        locations = json.loads(request.args.get("locations", "[]"))
        job_type = request.args.get("job_type", "Full-Time")
        include_h1b = request.args.get("include_h1b", "false").lower() == "true"
        
        weights = {
            'company_weight': float(request.args.get("overall_company_weight", 33)) / 100,
            'role_weight': float(request.args.get("overall_role_weight", 33)) / 100,
            'location_weight': float(request.args.get("overall_location_weight", 34)) / 100
        }
        
        # Validate weights
        total_weight = sum(weights.values()) * 100
        if abs(total_weight - 100) > 0.01:
            return jsonify({"error": f"Weights must sum to 100%. Current: {total_weight:.2f}%"}), 400
        
        # Search jobs
        jobs = job_db.search_jobs(companies, roles, locations, job_type)
        
        # Debug logging
        logger.info(f"Search criteria - Companies: {companies}, Roles: {roles}, Locations: {locations}, Job type: {job_type}")
        logger.info(f"Found {len(jobs)} jobs matching criteria")
        
        if not jobs:
            return jsonify({
                "error": "No jobs found matching your criteria",
                "search_criteria": {
                    "companies": companies,
                    "roles": roles, 
                    "locations": locations,
                    "job_type": job_type
                },
                "suggestion": "Try using broader search terms or check /debug_companies for available options"
            }), 404
        
        # Calculate match scores
        scored_jobs = job_matcher.calculate_job_scores(jobs, companies, roles, locations, weights)
        
        # Limit to top 200 for performance
        scored_jobs = scored_jobs[:200]
        
        # Add H1B predictions if requested
        if include_h1b:
            for job in scored_jobs:
                h1b_prob = h1b_predictor.predict_probability(job['company_name'], job['job_title'])
                job['h1b_sponsorship_probability'] = f"{h1b_prob}%"
        
        # Prepare data for Excel
        excel_data = []
        for job in scored_jobs:
            row = {
                'Job Title': job['job_title'],
                'Company Name': job['company_name'],
                'Location': job['location'],
                'Job Link': job['job_link'],
                'Work Type': job['work_type'],
                'Salary': job['salary'],
                'Source': job['source'],
                'Match Score': f"{job['match_score']}%"
            }
            
            if include_h1b:
                row['H1B Sponsorship Probability'] = job.get('h1b_sponsorship_probability', 'N/A')
            
            excel_data.append(row)
        
        # Create Excel file in memory
        df = pd.DataFrame(excel_data)
        
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Job Matches', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Job Matches']
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).str.len().max(), len(str(col)))
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        excel_buffer.seek(0)
        
        processing_time = time.time() - start_time
        logger.info(f"Request processed in {processing_time:.3f} seconds with {len(scored_jobs)} jobs")
        
        return send_file(
            excel_buffer,
            as_attachment=True,
            download_name=f"job_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error after {processing_time:.3f} seconds: {e}")
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "database_initialized": job_db.initialized,
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics."""
    try:
        conn = sqlite3.connect(job_db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM jobs')
        job_count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            "total_jobs": job_count,
            "h1b_companies": len(h1b_predictor.h1b_sponsors),
            "system_status": "optimized"
        })
    except:
        return jsonify({"error": "Stats unavailable"}), 500

@app.route('/test_h1b', methods=['GET'])
def test_h1b():
    """Test H1B prediction functionality."""
    try:
        company = request.args.get('company', 'Google')
        role = request.args.get('role', 'Software Engineer')

        prediction = h1b_predictor.predict_probability(company, role)

        return jsonify({
            "company": company,
            "role": role,
            "h1b_probability": f"{prediction}%",
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ip_info', methods=['GET'])
def ip_info():
    """Get current outbound IP and network information."""
    try:
        import requests as ip_requests
        
        # Get current outbound IP
        try:
            ip_response = ip_requests.get('https://api.ipify.org', timeout=10)
            current_ip = ip_response.text if ip_response.ok else 'Unable to determine'
        except:
            current_ip = 'Unable to determine'
        
        # Render's documented static IPs
        render_static_ips = [
            "44.226.145.213",
            "54.187.200.255", 
            "34.213.214.55",
            "35.164.95.156",
            "44.230.95.183",
            "44.229.200.200"
        ]
        
        return jsonify({
            "current_outbound_ip": current_ip,
            "render_static_ips": render_static_ips,
            "ip_in_static_range": current_ip in render_static_ips,
            "network_info": {
                "platform": "Render.com",
                "region": "US-West",
                "documentation": "See RENDER_NETWORK_INFO.md"
            },
            "status": "success"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/debug_companies', methods=['GET'])
def debug_companies():
    """Debug endpoint to see available companies in database."""
    try:
        # Simple check first
        if not hasattr(job_db, 'db_path') or not job_db.db_path:
            return jsonify({"error": "Database not initialized", "status": "error"}), 500
            
        conn = sqlite3.connect(job_db.db_path)
        cursor = conn.cursor()
        
        # Get total count first (simplest query)
        cursor.execute('SELECT COUNT(*) FROM jobs')
        total_jobs = cursor.fetchone()[0]
        
        if total_jobs == 0:
            conn.close()
            return jsonify({
                "total_jobs": 0,
                "message": "Database is empty - no jobs found",
                "status": "warning"
            })
        
        # Get unique companies (limit to prevent memory issues)
        cursor.execute('SELECT DISTINCT company_name FROM jobs ORDER BY company_name LIMIT 20')
        companies = [row[0] for row in cursor.fetchall()]
        
        # Get sample job titles
        cursor.execute('SELECT DISTINCT job_title FROM jobs ORDER BY job_title LIMIT 10')
        job_titles = [row[0] for row in cursor.fetchall()]
        
        # Get sample locations
        cursor.execute('SELECT DISTINCT location FROM jobs ORDER BY location LIMIT 10')
        locations = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            "total_jobs": total_jobs,
            "sample_companies": companies[:10],  # Limit response size
            "sample_job_titles": job_titles[:5],
            "sample_locations": locations[:5],
            "status": "success"
        })
    except Exception as e:
        logger.error(f"Debug companies error: {e}")
        return jsonify({"error": f"Database error: {str(e)}"}, "status": "error"), 500

# Initialize on startup
def initialize_app():
    """Initialize the application."""
    try:
        job_db.initialize()
        logger.info("Fast job API ready!")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize app: {e}")
        return False

if __name__ == '__main__':
    # Initialize database
    if initialize_app():
        logger.info("Starting Flask server...")
        # Run the app
        app.run(
            debug=False,
            host='0.0.0.0',
            port=5000,
            threaded=True
        )
    else:
        logger.error("Failed to initialize application. Exiting.")
        sys.exit(1)