import os
import sys
import sqlite3
import json
import random
import logging
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

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
        """Populate database with sample data."""
        companies = ['Google', 'Microsoft', 'Amazon', 'Apple', 'Meta']
        job_titles = ['Software Engineer', 'Data Scientist', 'Product Manager']
        locations = ['San Francisco, CA', 'New York, NY', 'Seattle, WA', 'Remote']
        work_types = ['Full-time', 'Remote']
        salaries = ['$120,000 - $160,000', '$160,000 - $200,000']
        sources = ['LinkedIn', 'Indeed']
        
        jobs_data = []
        for i in range(100):  # Generate 100 sample jobs for faster initialization
            company = random.choice(companies)
            title = random.choice(job_titles)
            location = random.choice(locations)
            work_type = random.choice(work_types)
            salary = random.choice(salaries)
            source = random.choice(sources)
            
            job_link = f'https://{source.lower()}.com/jobs/{company.lower()}-{title.lower().replace(" ", "-")}-{i}'
            
            jobs_data.append((title, company, location, job_link, work_type, salary, source))
        
        cursor.executemany('''
            INSERT INTO jobs (job_title, company_name, location, job_link, work_type, salary, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', jobs_data)
        
        logger.info(f"Populated database with {len(jobs_data)} sample jobs")
    
    def search_jobs(self, companies=None, roles=None, locations=None, job_type='Full-time', limit=50):
        """Simple job search."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Simple query for testing
            query = '''
                SELECT job_title, company_name, location, job_link, work_type, salary, source
                FROM jobs
                ORDER BY created_at DESC
                LIMIT ?
            '''
            
            cursor.execute(query, (limit,))
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
    """Main job search endpoint."""
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
        
        return jsonify({
            'jobs': jobs,
            'total_found': len(jobs),
            'h1b_enabled': include_h1b
        })
        
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