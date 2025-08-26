import asyncio
import sqlite3
import pandas as pd
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import hashlib
import os
import logging
from concurrent.futures import ThreadPoolExecutor
import json

try:
    import aiosqlite
except ImportError:
    aiosqlite = None

try:
    import polars as pl
except ImportError:
    pl = None

logger = logging.getLogger(__name__)

class DataOptimizer:
    """High-performance data layer with optimized queries and caching."""
    
    def __init__(self):
        self.db_path = 'jobs_database.db'
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.sample_jobs = []
        
    def initialize(self):
        """Initialize the database and create optimized indexes."""
        try:
            # Create database and tables
            self._create_database()
            
            # Populate with sample data if empty
            if self._is_database_empty():
                self._populate_sample_data()
            
            logger.info("Data optimizer initialized successfully")
            
        except Exception as e:
            logger.error(f"Data optimizer initialization error: {e}")
    
    def _create_database(self):
        """Create optimized database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create jobs table with optimized schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_title TEXT NOT NULL,
                    company_name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    job_link TEXT,
                    work_type TEXT DEFAULT 'Full-time',
                    salary TEXT DEFAULT 'N/A',
                    description TEXT DEFAULT '',
                    posted_date TEXT DEFAULT '',
                    source TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create optimized indexes for fast filtering
            indexes = [
                'CREATE INDEX IF NOT EXISTS idx_company_name ON jobs(company_name)',
                'CREATE INDEX IF NOT EXISTS idx_job_title ON jobs(job_title)',
                'CREATE INDEX IF NOT EXISTS idx_location ON jobs(location)',
                'CREATE INDEX IF NOT EXISTS idx_work_type ON jobs(work_type)',
                'CREATE INDEX IF NOT EXISTS idx_source ON jobs(source)',
                'CREATE INDEX IF NOT EXISTS idx_created_at ON jobs(created_at)',
                'CREATE INDEX IF NOT EXISTS idx_company_title ON jobs(company_name, job_title)',
                'CREATE INDEX IF NOT EXISTS idx_location_title ON jobs(location, job_title)',
                'CREATE INDEX IF NOT EXISTS idx_full_search ON jobs(company_name, job_title, location)'
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            # Create H1B predictions cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS h1b_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    job_title TEXT NOT NULL,
                    prediction_score REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(company_name, job_title)
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_h1b_company_role ON h1b_predictions(company_name, job_title)')
            
            conn.commit()
    
    def _is_database_empty(self) -> bool:
        """Check if database is empty."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM jobs')
            count = cursor.fetchone()[0]
            return count == 0
    
    def _populate_sample_data(self):
        """Populate database with sample job data for instant responses."""
        logger.info("Populating database with sample job data...")
        
        sample_data = self._generate_sample_jobs()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert sample jobs
            cursor.executemany('''
                INSERT INTO jobs (job_title, company_name, location, job_link, work_type, salary, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', sample_data)
            
            conn.commit()
            
        logger.info(f"Populated database with {len(sample_data)} sample jobs")
    
    def _generate_sample_jobs(self) -> List[Tuple]:
        """Generate realistic sample job data."""
        companies = [
            ('Google', 'tech'),
            ('Microsoft', 'tech'),
            ('Amazon', 'tech'),
            ('Apple', 'tech'),
            ('Meta', 'tech'),
            ('Netflix', 'tech'),
            ('Tesla', 'tech'),
            ('NVIDIA', 'tech'),
            ('Intel', 'tech'),
            ('Cisco', 'tech'),
            ('Goldman Sachs', 'finance'),
            ('JPMorgan Chase', 'finance'),
            ('Bank of America', 'finance'),
            ('Wells Fargo', 'finance'),
            ('Accenture', 'consulting'),
            ('Deloitte', 'consulting'),
            ('McKinsey & Company', 'consulting'),
            ('Boston Consulting Group', 'consulting'),
            ('Uber', 'tech'),
            ('Airbnb', 'tech'),
            ('Salesforce', 'tech'),
            ('Adobe', 'tech'),
            ('Oracle', 'tech'),
            ('IBM', 'tech'),
            ('Qualcomm', 'tech')
        ]
        
        job_titles = {
            'tech': [
                'Software Engineer',
                'Senior Software Engineer',
                'Principal Software Engineer',
                'Data Scientist',
                'Machine Learning Engineer',
                'Backend Engineer',
                'Frontend Engineer',
                'Full Stack Engineer',
                'DevOps Engineer',
                'Cloud Engineer',
                'Site Reliability Engineer',
                'Product Manager',
                'Technical Program Manager',
                'Engineering Manager',
                'Solutions Architect',
                'Security Engineer',
                'Data Engineer',
                'Platform Engineer',
                'Mobile Engineer',
                'AI Engineer'
            ],
            'finance': [
                'Software Developer',
                'Quantitative Analyst',
                'Risk Analyst',
                'Investment Banking Analyst',
                'Financial Analyst',
                'Portfolio Manager',
                'Compliance Officer',
                'Data Scientist',
                'Technology Analyst',
                'Vice President',
                'Director',
                'Managing Director'
            ],
            'consulting': [
                'Business Analyst',
                'Senior Consultant',
                'Principal Consultant',
                'Manager',
                'Senior Manager',
                'Director',
                'Partner',
                'Data Scientist',
                'Technology Consultant',
                'Strategy Consultant'
            ]
        }
        
        locations = [
            'San Francisco, CA',
            'New York, NY',
            'Seattle, WA',
            'Austin, TX',
            'Boston, MA',
            'Chicago, IL',
            'Los Angeles, CA',
            'Denver, CO',
            'Atlanta, GA',
            'Raleigh, NC',
            'Remote',
            'Mountain View, CA',
            'Palo Alto, CA',
            'Redmond, WA',
            'Cambridge, MA'
        ]
        
        work_types = ['Full-time', 'Part-time', 'Contract', 'Remote', 'Hybrid']
        
        salary_ranges = [
            '$80,000 - $120,000',
            '$120,000 - $160,000',
            '$160,000 - $200,000',
            '$200,000 - $250,000',
            '$250,000 - $300,000',
            '$300,000+',
            'Competitive',
            'N/A'
        ]
        
        sources = ['LinkedIn', 'Indeed', 'Glassdoor']
        
        sample_jobs = []
        
        # Generate jobs for each company
        for company, category in companies:
            company_titles = job_titles[category]
            
            # Generate 15-25 jobs per company
            for i in range(15, 26):
                import random
                
                title = random.choice(company_titles)
                location = random.choice(locations)
                work_type = random.choice(work_types)
                salary = random.choice(salary_ranges)
                source = random.choice(sources)
                
                # Generate realistic job link
                job_link = f'https://{source.lower()}.com/jobs/{company.lower().replace(" ", "-")}-{title.lower().replace(" ", "-")}-{i}'
                
                sample_jobs.append((
                    title,
                    company,
                    location,
                    job_link,
                    work_type,
                    salary,
                    source
                ))
        
        return sample_jobs
    
    async def get_filtered_jobs(self, params: Dict) -> Optional[List[Dict]]:
        """Get filtered jobs from database with optimized queries."""
        try:
            companies = params.get('companies', [])
            roles = params.get('roles', [])
            locations = params.get('locations', [])
            job_type = params.get('job_type', 'Full-Time')
            
            # Build optimized query with indexes
            base_query = '''
                SELECT job_title, company_name, location, job_link, work_type, salary, source
                FROM jobs
                WHERE 1=1
            '''
            
            query_params = []
            conditions = []
            
            # Company filter
            if companies and not (len(companies) == 1 and companies[0].get('company') == 'any'):
                company_conditions = []
                for company in companies:
                    if company.get('company') and company['company'] != 'any':
                        company_conditions.append('company_name LIKE ?')
                        query_params.append(f"%{company['company']}%")
                
                if company_conditions:
                    conditions.append(f"({' OR '.join(company_conditions)})")
            
            # Role filter
            if roles and not (len(roles) == 1 and roles[0].get('role') == 'any'):
                role_conditions = []
                for role in roles:
                    if role.get('role') and role['role'] != 'any':
                        role_conditions.append('job_title LIKE ?')
                        query_params.append(f"%{role['role']}%")
                
                if role_conditions:
                    conditions.append(f"({' OR '.join(role_conditions)})")
            
            # Location filter
            if locations and not (len(locations) == 1 and locations[0].get('location') == 'any'):
                location_conditions = []
                for location in locations:
                    if location.get('location') and location['location'] != 'any':
                        location_conditions.append('location LIKE ?')
                        query_params.append(f"%{location['location']}%")
                
                if location_conditions:
                    conditions.append(f"({' OR '.join(location_conditions)})")
            
            # Job type filter
            if job_type and job_type.lower() != 'any':
                conditions.append('work_type LIKE ?')
                query_params.append(f"%{job_type}%")
            
            # Combine conditions
            if conditions:
                base_query += ' AND ' + ' AND '.join(conditions)
            
            # Order by and limit for performance
            base_query += ' ORDER BY created_at DESC LIMIT 500'
            
            # Execute query asynchronously
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(base_query, query_params) as cursor:
                    rows = await cursor.fetchall()
                    
                    if rows:
                        columns = ['job_title', 'company_name', 'location', 'job_link', 'work_type', 'salary', 'source']
                        jobs = [dict(zip(columns, row)) for row in rows]
                        return jobs
            
            return None
            
        except Exception as e:
            logger.error(f"Database query error: {e}")
            return None
    
    async def get_general_jobs(self, params: Dict, limit: int = 100) -> List[Dict]:
        """Get general jobs as fallback when no specific matches found."""
        try:
            # Get recent jobs with variety
            query = '''
                SELECT job_title, company_name, location, job_link, work_type, salary, source
                FROM jobs
                ORDER BY created_at DESC
                LIMIT ?
            '''
            
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(query, (limit,)) as cursor:
                    rows = await cursor.fetchall()
                    
                    if rows:
                        columns = ['job_title', 'company_name', 'location', 'job_link', 'work_type', 'salary', 'source']
                        jobs = [dict(zip(columns, row)) for row in rows]
                        return jobs
            
            return []
            
        except Exception as e:
            logger.error(f"General jobs query error: {e}")
            return []
    
    async def insert_jobs_batch(self, jobs: List[Dict]) -> bool:
        """Insert multiple jobs efficiently using batch operations."""
        try:
            if not jobs:
                return True
            
            # Prepare data for insertion
            job_data = []
            for job in jobs:
                job_data.append((
                    job.get('job_title', ''),
                    job.get('company_name', ''),
                    job.get('location', ''),
                    job.get('job_link', ''),
                    job.get('work_type', 'Full-time'),
                    job.get('salary', 'N/A'),
                    job.get('source', '')
                ))
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.executemany('''
                    INSERT OR REPLACE INTO jobs 
                    (job_title, company_name, location, job_link, work_type, salary, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', job_data)
                
                await db.commit()
            
            logger.info(f"Inserted {len(jobs)} jobs into database")
            return True
            
        except Exception as e:
            logger.error(f"Batch insert error: {e}")
            return False
    
    async def cache_h1b_prediction(self, company: str, role: str, prediction: float) -> bool:
        """Cache H1B prediction in database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR REPLACE INTO h1b_predictions (company_name, job_title, prediction_score)
                    VALUES (?, ?, ?)
                ''', (company, role, prediction))
                
                await db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"H1B cache error: {e}")
            return False
    
    async def get_h1b_prediction(self, company: str, role: str) -> Optional[float]:
        """Get cached H1B prediction from database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT prediction_score FROM h1b_predictions
                    WHERE company_name = ? AND job_title = ?
                ''', (company, role)) as cursor:
                    
                    row = await cursor.fetchone()
                    if row:
                        return row[0]
            
            return None
            
        except Exception as e:
            logger.error(f"H1B prediction get error: {e}")
            return None
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics for monitoring."""
        try:
            stats = {}
            
            async with aiosqlite.connect(self.db_path) as db:
                # Job counts
                async with db.execute('SELECT COUNT(*) FROM jobs') as cursor:
                    row = await cursor.fetchone()
                    stats['total_jobs'] = row[0] if row else 0
                
                # Company counts
                async with db.execute('SELECT COUNT(DISTINCT company_name) FROM jobs') as cursor:
                    row = await cursor.fetchone()
                    stats['unique_companies'] = row[0] if row else 0
                
                # Location counts
                async with db.execute('SELECT COUNT(DISTINCT location) FROM jobs') as cursor:
                    row = await cursor.fetchone()
                    stats['unique_locations'] = row[0] if row else 0
                
                # H1B predictions
                async with db.execute('SELECT COUNT(*) FROM h1b_predictions') as cursor:
                    row = await cursor.fetchone()
                    stats['h1b_predictions_cached'] = row[0] if row else 0
                
                # Recent jobs
                async with db.execute('''
                    SELECT COUNT(*) FROM jobs 
                    WHERE created_at > datetime('now', '-24 hours')
                ''') as cursor:
                    row = await cursor.fetchone()
                    stats['jobs_last_24h'] = row[0] if row else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Database stats error: {e}")
            return {}
    
    async def cleanup_old_data(self, days: int = 30) -> bool:
        """Clean up old job data to maintain performance."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Remove old jobs
                await db.execute('''
                    DELETE FROM jobs 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days))
                
                # Remove old H1B predictions
                await db.execute('''
                    DELETE FROM h1b_predictions 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days * 2))  # Keep H1B predictions longer
                
                await db.commit()
            
            logger.info(f"Cleaned up data older than {days} days")
            return True
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return False