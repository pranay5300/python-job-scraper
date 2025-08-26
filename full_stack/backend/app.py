import os
import sys
import sqlite3
import json
import random
import logging
import io
from datetime import datetime

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openpyxl import Workbook

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configure CORS for development and production
CORS(app, resources={
    r"/*": {"origins": "*"}
})

class FastJobDatabase:
    """Fast job database with SQLite persistence."""
    
    def __init__(self):
        self.db_path = 'fast_jobs.db'
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
            
            # Check if we need to populate
            cursor.execute('SELECT COUNT(*) FROM jobs')
            count = cursor.fetchone()[0]
            
            if count == 0:
                self._populate_sample_data(cursor)
            
            conn.commit()
            conn.close()
            self.initialized = True
            logger.info("Fast job database initialized")
            return True
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            return False
    
    def _populate_sample_data(self, cursor):
        """Populate database with diverse sample data."""
        companies = [
            'Google', 'Microsoft', 'Amazon', 'Apple', 'Meta', 'Netflix', 'Tesla',
            'NVIDIA', 'Intel', 'Cisco', 'Oracle', 'IBM', 'Salesforce', 'Adobe',
            'Uber', 'Airbnb', 'Spotify', 'LinkedIn', 'Twitter', 'Snap',
            'Goldman Sachs', 'JPMorgan Chase', 'Bank of America', 'Wells Fargo',
            'Accenture', 'Deloitte', 'McKinsey & Company', 'BCG', 'Bain & Company',
            'Walmart', 'Target', 'Costco', 'Home Depot', 'Lowe\'s', 'FedEx', 'UPS'
        ]
        
        job_titles = [
            # Tech roles
            'Software Engineer', 'Senior Software Engineer', 'Data Scientist', 'Machine Learning Engineer',
            'Product Manager', 'Technical Program Manager', 'Engineering Manager', 'DevOps Engineer',
            'Cloud Engineer', 'Security Engineer', 'Frontend Engineer', 'Backend Engineer',
            'Full Stack Engineer', 'Mobile Engineer', 'QA Engineer', 'Solutions Architect',
            # Business roles
            'Operations Manager', 'Supply Chain Analyst', 'Business Analyst', 'Project Manager',
            'Marketing Manager', 'Sales Manager', 'Finance Manager', 'HR Manager',
            'Operations Analyst', 'Supply Chain Manager', 'Business Development Manager',
            'Strategy Manager', 'Product Marketing Manager', 'Customer Success Manager',
            # Finance roles
            'Financial Analyst', 'Investment Analyst', 'Risk Analyst', 'Credit Analyst',
            'Treasury Analyst', 'Corporate Finance Manager', 'Investment Banking Analyst',
            # Consulting roles
            'Management Consultant', 'Strategy Consultant', 'Technology Consultant',
            'Operations Consultant', 'Financial Consultant',
            # Other roles
            'Data Analyst', 'Marketing Analyst', 'Sales Representative', 'Account Manager',
            'Customer Service Representative', 'Administrative Assistant', 'Executive Assistant'
        ]
        
        locations = [
            'San Francisco, CA', 'New York, NY', 'Seattle, WA', 'Austin, TX',
            'Boston, MA', 'Chicago, IL', 'Los Angeles, CA', 'Denver, CO',
            'Atlanta, GA', 'Raleigh, NC', 'Remote', 'Mountain View, CA',
            'Palo Alto, CA', 'Redmond, WA', 'Cambridge, MA', 'Dallas, TX',
            'Houston, TX', 'Phoenix, AZ', 'Philadelphia, PA', 'San Diego, CA'
        ]
        
        work_types = ['Full-time', 'Part-time', 'Contract', 'Remote', 'Hybrid', 'Internship']
        salaries = [
            '$60,000 - $80,000', '$80,000 - $120,000', '$120,000 - $160,000', 
            '$160,000 - $200,000', '$200,000 - $250,000', '$250,000+',
            'Competitive', 'N/A'
        ]
        sources = ['LinkedIn', 'Indeed', 'Glassdoor', 'Company Website']
        
        jobs_data = []
        for i in range(200):  # Generate 200 diverse sample jobs
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
        
        logger.info(f"Populated database with {len(jobs_data)} diverse sample jobs")
    
    def search_jobs(self, companies=None, roles=None, locations=None, job_type='Full-time', limit=50):
        """Accurate job search with proper filtering."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build WHERE conditions
            where_conditions = []
            params = []
            
            # Company filter - exact match or partial match
            if companies and len(companies) > 0:
                company_conditions = []
                for company in companies:
                    if company.get('company') and company['company'].lower() not in ['any', '']:
                        company_name = company['company'].strip()
                        # Try exact match first, then partial match
                        company_conditions.append('(LOWER(company_name) = ? OR LOWER(company_name) LIKE ?)')
                        params.extend([company_name.lower(), f'%{company_name.lower()}%'])
                
                if company_conditions:
                    where_conditions.append(f"({' OR '.join(company_conditions)})")
            
            # Role filter - exact match or keyword match
            if roles and len(roles) > 0:
                role_conditions = []
                for role in roles:
                    if role.get('role') and role['role'].lower() not in ['any', '']:
                        role_name = role['role'].strip()
                        # Try exact match first, then keyword match
                        role_conditions.append('(LOWER(job_title) = ? OR LOWER(job_title) LIKE ?)')
                        params.extend([role_name.lower(), f'%{role_name.lower()}%'])
                
                if role_conditions:
                    where_conditions.append(f"({' OR '.join(role_conditions)})")
            
            # Location filter - exact match or partial match
            if locations and len(locations) > 0:
                location_conditions = []
                for location in locations:
                    if location.get('location') and location['location'].lower() not in ['any', '']:
                        location_name = location['location'].strip()
                        # Try exact match first, then partial match
                        location_conditions.append('(LOWER(location) = ? OR LOWER(location) LIKE ?)')
                        params.extend([location_name.lower(), f'%{location_name.lower()}%'])
                
                if location_conditions:
                    where_conditions.append(f"({' OR '.join(location_conditions)})")
            
            # Job type filter - exact match
            if job_type and job_type.lower() not in ['any', '']:
                where_conditions.append('LOWER(work_type) = ?')
                params.append(job_type.lower())
            
            # Build final query
            query = '''
                SELECT job_title, company_name, location, job_link, work_type, salary, source
                FROM jobs
            '''
            
            if where_conditions:
                query += ' WHERE ' + ' AND '.join(where_conditions)
            
            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            jobs = []
            for row in results:
                jobs.append({
                    'job_title': row[0],
                    'company_name': row[1],
                    'location': row[2],
                    'job_link': row[3],
                    'work_type': row[4],
                    'salary': row[5],
                    'source': row[6]
                })
            
            logger.info(f"Search found {len(jobs)} jobs with filters: companies={companies}, roles={roles}, locations={locations}, job_type={job_type}")
            return jobs
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

class FastH1BPredictor:
    """Simple H1B sponsorship predictor."""
    
    def __init__(self):
        pass
    
    def predict_probability(self, company, role):
        """Predict H1B sponsorship probability."""
        company_lower = company.lower()
        
        # Simple mock H1B prediction
        if company_lower in ['google', 'microsoft', 'amazon']:
            return 85
        else:
            return 45

# Initialize components
job_db = FastJobDatabase()
h1b_predictor = FastH1BPredictor()

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
            "download_excel": "/download_excel"
        },
        "production_url": "https://python-job-scraper.onrender.com",
        "frontend_compatible": True,
        "cors_enabled": True
    })

@app.route('/download_excel', methods=['GET'])
def download_excel():
    """Main job search endpoint with Excel generation."""
    try:
        # Get parameters
        companies = request.args.get('companies', '[]')
        roles = request.args.get('roles', '[]')
        locations = request.args.get('locations', '[]')
        job_type = request.args.get('job_type', 'Full-time')
        include_h1b = request.args.get('include_h1b', 'false').lower() == 'true'
        
        # Parse JSON parameters
        try:
            companies = json.loads(companies) if companies else []
            roles = json.loads(roles) if roles else []
            locations = json.loads(locations) if locations else []
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON parameters'}), 400
        
        # Search jobs
        jobs = job_db.search_jobs(companies, roles, locations, job_type)
        
        # Add H1B predictions if requested
        if include_h1b:
            for job in jobs:
                company = job['company_name']
                h1b_probability = h1b_predictor.predict_probability(company, job['job_title'])
                job['h1b_probability'] = h1b_probability
        
        # Create Excel file
        wb = Workbook()
        ws = wb.active
        ws.title = "Job Matches"
        
        # Add headers
        headers = ['Job Title', 'Company Name', 'Location', 'Job Link', 'Work Type', 'Salary', 'Source']
        if include_h1b:
            headers.append('H1B Probability')
        
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
        
        # Add job data
        for row, job in enumerate(jobs, 2):
            ws.cell(row=row, column=1, value=job['job_title'])
            ws.cell(row=row, column=2, value=job['company_name'])
            ws.cell(row=row, column=3, value=job['location'])
            ws.cell(row=row, column=4, value=job['job_link'])
            ws.cell(row=row, column=5, value=job['work_type'])
            ws.cell(row=row, column=6, value=job['salary'])
            ws.cell(row=row, column=7, value=job['source'])
            if include_h1b:
                ws.cell(row=row, column=8, value=f"{job.get('h1b_probability', 'N/A')}%")
        
        # Save to memory
        excel_buffer = io.BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)
        
        # Return Excel file
        return send_file(
            excel_buffer,
            as_attachment=True,
            download_name=f"job_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error(f"Job search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'database_initialized': job_db.initialized,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get database statistics."""
    try:
        conn = sqlite3.connect(job_db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM jobs')
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'total_jobs': count,
            'database_initialized': job_db.initialized
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test_h1b', methods=['GET'])
def test_h1b():
    """Test H1B prediction endpoint."""
    company = request.args.get('company', 'Unknown')
    role = request.args.get('role', 'Unknown')
    
    # Simple mock H1B prediction
    h1b_probability = h1b_predictor.predict_probability(company, role)
    
    return jsonify({
        'company': company,
        'role': role,
        'h1b_probability': h1b_probability
    })

def initialize_app():
    """Initialize the application."""
    try:
        success = job_db.initialize()
        if success:
            logger.info("Job API ready!")
        return success
    except Exception as e:
        logger.error(f"Failed to initialize app: {e}")
        return False

if __name__ == '__main__':
    # Initialize database
    if initialize_app():
        logger.info("Starting Flask server...")
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            threaded=True
        )
    else:
        logger.error("Failed to initialize application. Exiting.")
        sys.exit(1)