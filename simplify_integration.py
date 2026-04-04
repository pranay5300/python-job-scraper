#!/usr/bin/env python3
"""
Simplify Integration Module
Integrates with Simplify platform for enhanced job matching and application tracking
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import time
import os
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class SimplifyJobMatch:
    job_id: str
    company: str
    title: str
    location: str
    match_score: float
    requirements_match: Dict
    application_url: str
    posted_date: str
    salary_range: str
    job_type: str
    experience_level: str
    skills_required: List[str]
    benefits: List[str]
    application_deadline: str

class SimplifyAPI:
    """Simplify API integration for job matching and applications"""
    
    def __init__(self, api_key: str = None, user_token: str = None):
        self.api_key = api_key or os.getenv('SIMPLIFY_API_KEY')
        self.user_token = user_token or os.getenv('SIMPLIFY_USER_TOKEN')
        self.base_url = "https://api.simplify.jobs/v1"
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'SupplyChain-AutoApply/1.0'
            })

    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with Simplify platform"""
        try:
            auth_data = {
                'email': email,
                'password': password
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=auth_data)
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data.get('token')
                self.session.headers.update({'Authorization': f'Bearer {self.user_token}'})
                logger.info("Successfully authenticated with Simplify")
                return True
            else:
                logger.error(f"Simplify authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error authenticating with Simplify: {e}")
            return False

    def get_user_profile(self) -> Dict:
        """Get user profile information from Simplify"""
        try:
            response = self.session.get(f"{self.base_url}/user/profile")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get user profile: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return {}

    def update_preferences(self, preferences: Dict) -> bool:
        """Update job search preferences"""
        try:
            # Supply chain specific preferences
            supply_chain_prefs = {
                'job_functions': [
                    'Supply Chain Management',
                    'Operations',
                    'Logistics',
                    'Procurement',
                    'Inventory Management',
                    'Demand Planning',
                    'Manufacturing',
                    'Distribution'
                ],
                'industries': [
                    'Manufacturing',
                    'Retail',
                    'E-commerce',
                    'Automotive',
                    'Aerospace',
                    'Consumer Goods',
                    'Technology',
                    'Healthcare',
                    'Food & Beverage'
                ],
                'keywords': [
                    'supply chain',
                    'logistics',
                    'operations',
                    'procurement',
                    'inventory',
                    'lean manufacturing',
                    'six sigma',
                    'ERP',
                    'SAP',
                    'demand planning',
                    'rotational program',
                    'leadership development'
                ],
                'experience_level': ['Entry Level', 'Associate'],
                'job_types': ['Full-time', 'Rotational Program'],
                'locations': ['United States'],
                'remote_work': True,
                'salary_range': {
                    'min': 60000,
                    'max': 120000
                }
            }
            
            # Merge with user preferences
            final_prefs = {**supply_chain_prefs, **preferences}
            
            response = self.session.put(f"{self.base_url}/user/preferences", json=final_prefs)
            
            if response.status_code == 200:
                logger.info("Successfully updated Simplify preferences")
                return True
            else:
                logger.error(f"Failed to update preferences: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            return False

    def search_jobs(self, query: str = "", filters: Dict = None) -> List[SimplifyJobMatch]:
        """Search for jobs on Simplify platform"""
        jobs = []
        
        try:
            # Default supply chain search parameters
            search_params = {
                'query': query or 'supply chain OR logistics OR operations',
                'location': 'United States',
                'job_type': 'full-time',
                'experience_level': 'entry-level',
                'posted_within': '7d',
                'limit': 50
            }
            
            if filters:
                search_params.update(filters)
            
            response = self.session.get(f"{self.base_url}/jobs/search", params=search_params)
            
            if response.status_code == 200:
                data = response.json()
                
                for job_data in data.get('jobs', []):
                    job_match = SimplifyJobMatch(
                        job_id=job_data.get('id', ''),
                        company=job_data.get('company', {}).get('name', ''),
                        title=job_data.get('title', ''),
                        location=job_data.get('location', ''),
                        match_score=job_data.get('match_score', 0.0),
                        requirements_match=job_data.get('requirements_match', {}),
                        application_url=job_data.get('application_url', ''),
                        posted_date=job_data.get('posted_date', ''),
                        salary_range=job_data.get('salary_range', ''),
                        job_type=job_data.get('job_type', ''),
                        experience_level=job_data.get('experience_level', ''),
                        skills_required=job_data.get('skills_required', []),
                        benefits=job_data.get('benefits', []),
                        application_deadline=job_data.get('application_deadline', '')
                    )
                    jobs.append(job_match)
                
                logger.info(f"Found {len(jobs)} jobs on Simplify")
                
            else:
                logger.error(f"Failed to search jobs: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error searching Simplify jobs: {e}")
        
        return jobs

    def get_job_details(self, job_id: str) -> Dict:
        """Get detailed information about a specific job"""
        try:
            response = self.session.get(f"{self.base_url}/jobs/{job_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get job details: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting job details: {e}")
            return {}

    def apply_to_job(self, job_id: str, cover_letter: str = "", additional_info: Dict = None) -> bool:
        """Apply to a job through Simplify platform"""
        try:
            application_data = {
                'job_id': job_id,
                'cover_letter': cover_letter,
                'additional_info': additional_info or {}
            }
            
            response = self.session.post(f"{self.base_url}/applications", json=application_data)
            
            if response.status_code == 201:
                logger.info(f"Successfully applied to job {job_id} via Simplify")
                return True
            else:
                logger.error(f"Failed to apply via Simplify: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error applying via Simplify: {e}")
            return False

    def get_application_status(self, application_id: str) -> Dict:
        """Get status of a submitted application"""
        try:
            response = self.session.get(f"{self.base_url}/applications/{application_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get application status: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting application status: {e}")
            return {}

    def get_my_applications(self) -> List[Dict]:
        """Get all user's applications"""
        try:
            response = self.session.get(f"{self.base_url}/applications/me")
            
            if response.status_code == 200:
                data = response.json()
                return data.get('applications', [])
            else:
                logger.error(f"Failed to get applications: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting applications: {e}")
            return []

    def upload_resume(self, resume_path: str) -> bool:
        """Upload resume to Simplify platform"""
        try:
            with open(resume_path, 'rb') as resume_file:
                files = {'resume': resume_file}
                response = self.session.post(f"{self.base_url}/user/resume", files=files)
                
                if response.status_code == 200:
                    logger.info("Successfully uploaded resume to Simplify")
                    return True
                else:
                    logger.error(f"Failed to upload resume: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error uploading resume: {e}")
            return False

    def get_recommended_jobs(self, limit: int = 25) -> List[SimplifyJobMatch]:
        """Get AI-recommended jobs based on profile"""
        jobs = []
        
        try:
            params = {'limit': limit}
            response = self.session.get(f"{self.base_url}/jobs/recommendations", params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                for job_data in data.get('recommendations', []):
                    job_match = SimplifyJobMatch(
                        job_id=job_data.get('job', {}).get('id', ''),
                        company=job_data.get('job', {}).get('company', {}).get('name', ''),
                        title=job_data.get('job', {}).get('title', ''),
                        location=job_data.get('job', {}).get('location', ''),
                        match_score=job_data.get('match_score', 0.0),
                        requirements_match=job_data.get('requirements_match', {}),
                        application_url=job_data.get('job', {}).get('application_url', ''),
                        posted_date=job_data.get('job', {}).get('posted_date', ''),
                        salary_range=job_data.get('job', {}).get('salary_range', ''),
                        job_type=job_data.get('job', {}).get('job_type', ''),
                        experience_level=job_data.get('job', {}).get('experience_level', ''),
                        skills_required=job_data.get('job', {}).get('skills_required', []),
                        benefits=job_data.get('job', {}).get('benefits', []),
                        application_deadline=job_data.get('job', {}).get('application_deadline', '')
                    )
                    jobs.append(job_match)
                
                logger.info(f"Got {len(jobs)} recommended jobs from Simplify")
                
            else:
                logger.error(f"Failed to get recommendations: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
        
        return jobs

    def track_application_progress(self) -> Dict:
        """Get comprehensive application tracking data"""
        try:
            response = self.session.get(f"{self.base_url}/analytics/applications")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get application analytics: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting application analytics: {e}")
            return {}

class SimplifyEnhancedMatcher:
    """Enhanced job matching using Simplify data"""
    
    def __init__(self, simplify_api: SimplifyAPI):
        self.simplify_api = simplify_api
        
    def analyze_job_compatibility(self, linkedin_job_details: Dict, 
                                 user_profile: Dict = None) -> Tuple[float, Dict]:
        """Analyze job compatibility using Simplify's AI"""
        try:
            if not user_profile:
                user_profile = self.simplify_api.get_user_profile()
            
            # Extract key information
            job_title = linkedin_job_details.get('title', '')
            job_description = linkedin_job_details.get('description', '')
            company = linkedin_job_details.get('company', '')
            location = linkedin_job_details.get('location', '')
            
            # Calculate compatibility score
            compatibility_score = self._calculate_compatibility_score(
                job_title, job_description, user_profile
            )
            
            # Extract requirements matching
            requirements_match = self._analyze_requirements_match(
                job_description, user_profile
            )
            
            analysis = {
                'compatibility_score': compatibility_score,
                'requirements_match': requirements_match,
                'recommended_action': 'apply' if compatibility_score > 0.7 else 'skip',
                'match_reasons': self._get_match_reasons(job_title, job_description),
                'skill_gaps': self._identify_skill_gaps(job_description, user_profile),
                'salary_estimate': self._estimate_salary_range(job_title, location, company)
            }
            
            return compatibility_score, analysis
            
        except Exception as e:
            logger.error(f"Error analyzing job compatibility: {e}")
            return 0.0, {}

    def _calculate_compatibility_score(self, job_title: str, job_description: str, 
                                     user_profile: Dict) -> float:
        """Calculate compatibility score between job and user profile"""
        score = 0.0
        
        # Supply chain keywords matching
        supply_chain_keywords = [
            'supply chain', 'logistics', 'operations', 'procurement', 'inventory',
            'distribution', 'manufacturing', 'planning', 'sourcing', 'vendor management'
        ]
        
        job_text = f"{job_title} {job_description}".lower()
        
        # Keyword matching (40% of score)
        keyword_matches = sum(1 for keyword in supply_chain_keywords if keyword in job_text)
        keyword_score = min(keyword_matches / len(supply_chain_keywords), 1.0) * 0.4
        score += keyword_score
        
        # Experience level matching (30% of score)
        experience_keywords = ['entry level', 'associate', 'junior', '0-2 years', 'new graduate']
        if any(keyword in job_text for keyword in experience_keywords):
            score += 0.3
        
        # Rotational program bonus (20% of score)
        rotational_keywords = ['rotational', 'leadership development', 'graduate program', 'trainee']
        if any(keyword in job_text for keyword in rotational_keywords):
            score += 0.2
        
        # Location preference (10% of score)
        user_locations = user_profile.get('preferred_locations', [])
        job_location = job_description.lower()
        if any(loc.lower() in job_location for loc in user_locations) or 'remote' in job_location:
            score += 0.1
        
        return min(score, 1.0)

    def _analyze_requirements_match(self, job_description: str, user_profile: Dict) -> Dict:
        """Analyze how well user matches job requirements"""
        requirements = {
            'education': self._check_education_match(job_description, user_profile),
            'experience': self._check_experience_match(job_description, user_profile),
            'skills': self._check_skills_match(job_description, user_profile),
            'certifications': self._check_certifications_match(job_description, user_profile)
        }
        
        return requirements

    def _check_education_match(self, job_description: str, user_profile: Dict) -> Dict:
        """Check education requirements match"""
        job_desc_lower = job_description.lower()
        user_education = user_profile.get('education', {})
        
        # Common education requirements
        if 'bachelor' in job_desc_lower:
            required_level = 'bachelor'
        elif 'master' in job_desc_lower or 'mba' in job_desc_lower:
            required_level = 'master'
        else:
            required_level = 'bachelor'  # Default assumption
        
        user_degree = user_education.get('highest_degree', '').lower()
        
        match = False
        if required_level == 'bachelor' and user_degree in ['bachelor', 'master', 'phd']:
            match = True
        elif required_level == 'master' and user_degree in ['master', 'mba', 'phd']:
            match = True
        
        return {
            'required': required_level,
            'user_has': user_degree,
            'match': match
        }

    def _check_experience_match(self, job_description: str, user_profile: Dict) -> Dict:
        """Check experience requirements match"""
        job_desc_lower = job_description.lower()
        
        # Extract experience requirements
        experience_required = 0
        if 'entry level' in job_desc_lower or 'new graduate' in job_desc_lower:
            experience_required = 0
        elif '1-2 years' in job_desc_lower or '0-2 years' in job_desc_lower:
            experience_required = 1
        elif '2-3 years' in job_desc_lower:
            experience_required = 2
        
        user_experience = user_profile.get('years_of_experience', 0)
        
        return {
            'required_years': experience_required,
            'user_years': user_experience,
            'match': user_experience >= experience_required
        }

    def _check_skills_match(self, job_description: str, user_profile: Dict) -> Dict:
        """Check skills requirements match"""
        # Common supply chain skills
        required_skills = []
        job_desc_lower = job_description.lower()
        
        skill_keywords = {
            'Excel': ['excel', 'spreadsheet'],
            'SAP': ['sap'],
            'SQL': ['sql', 'database'],
            'Python': ['python'],
            'Lean': ['lean', 'lean manufacturing'],
            'Six Sigma': ['six sigma'],
            'Project Management': ['project management', 'pmp'],
            'Data Analysis': ['data analysis', 'analytics'],
            'ERP': ['erp'],
            'Supply Chain': ['supply chain management']
        }
        
        for skill, keywords in skill_keywords.items():
            if any(keyword in job_desc_lower for keyword in keywords):
                required_skills.append(skill)
        
        user_skills = user_profile.get('skills', [])
        matched_skills = [skill for skill in required_skills if skill.lower() in [s.lower() for s in user_skills]]
        
        return {
            'required_skills': required_skills,
            'user_skills': user_skills,
            'matched_skills': matched_skills,
            'match_percentage': len(matched_skills) / len(required_skills) if required_skills else 1.0
        }

    def _check_certifications_match(self, job_description: str, user_profile: Dict) -> Dict:
        """Check certifications requirements match"""
        job_desc_lower = job_description.lower()
        
        relevant_certs = []
        cert_keywords = {
            'PMP': ['pmp', 'project management professional'],
            'Six Sigma': ['six sigma', 'lean six sigma'],
            'APICS': ['apics', 'scor'],
            'CPSM': ['cpsm', 'certified professional in supply management']
        }
        
        for cert, keywords in cert_keywords.items():
            if any(keyword in job_desc_lower for keyword in keywords):
                relevant_certs.append(cert)
        
        user_certs = user_profile.get('certifications', [])
        matched_certs = [cert for cert in relevant_certs if cert.lower() in [c.lower() for c in user_certs]]
        
        return {
            'relevant_certifications': relevant_certs,
            'user_certifications': user_certs,
            'matched_certifications': matched_certs
        }

    def _get_match_reasons(self, job_title: str, job_description: str) -> List[str]:
        """Get reasons why this job is a good match"""
        reasons = []
        job_text = f"{job_title} {job_description}".lower()
        
        if 'rotational' in job_text:
            reasons.append("Rotational program opportunity")
        
        if 'leadership development' in job_text:
            reasons.append("Leadership development program")
        
        if 'supply chain' in job_text:
            reasons.append("Direct supply chain focus")
        
        if 'entry level' in job_text or 'new graduate' in job_text:
            reasons.append("Entry-level position suitable for new graduates")
        
        if any(keyword in job_text for keyword in ['fortune 500', 'global company', 'multinational']):
            reasons.append("Large, established company")
        
        return reasons

    def _identify_skill_gaps(self, job_description: str, user_profile: Dict) -> List[str]:
        """Identify skills that user should develop"""
        job_desc_lower = job_description.lower()
        user_skills = [skill.lower() for skill in user_profile.get('skills', [])]
        
        important_skills = {
            'Excel': ['excel', 'advanced excel'],
            'SQL': ['sql', 'database'],
            'Python': ['python', 'programming'],
            'Tableau': ['tableau', 'data visualization'],
            'SAP': ['sap'],
            'Project Management': ['project management'],
            'Lean Six Sigma': ['lean', 'six sigma']
        }
        
        skill_gaps = []
        for skill, keywords in important_skills.items():
            if any(keyword in job_desc_lower for keyword in keywords):
                if skill.lower() not in user_skills:
                    skill_gaps.append(skill)
        
        return skill_gaps

    def _estimate_salary_range(self, job_title: str, location: str, company: str) -> str:
        """Estimate salary range based on job details"""
        # Basic salary estimation logic
        base_salary = 65000  # Base for supply chain entry level
        
        # Title adjustments
        title_lower = job_title.lower()
        if 'senior' in title_lower:
            base_salary += 20000
        elif 'manager' in title_lower:
            base_salary += 15000
        elif 'analyst' in title_lower:
            base_salary += 5000
        
        # Location adjustments
        location_lower = location.lower()
        high_cost_areas = ['new york', 'san francisco', 'seattle', 'boston', 'washington dc']
        if any(area in location_lower for area in high_cost_areas):
            base_salary += 15000
        
        # Company size adjustment (approximate)
        if company.lower() in ['amazon', 'apple', 'google', 'microsoft', 'meta']:
            base_salary += 20000
        
        salary_range = f"${base_salary - 5000:,} - ${base_salary + 15000:,}"
        return salary_range

def integrate_simplify_with_linkedin(linkedin_auto_apply, simplify_api: SimplifyAPI):
    """Integrate Simplify recommendations with LinkedIn auto-apply"""
    
    # Get Simplify recommendations
    recommended_jobs = simplify_api.get_recommended_jobs(limit=50)
    
    # Create enhanced matcher
    matcher = SimplifyEnhancedMatcher(simplify_api)
    
    # Process each recommendation
    enhanced_applications = []
    
    for simplify_job in recommended_jobs:
        if simplify_job.match_score > 0.7:  # High match score threshold
            
            # Convert Simplify job to LinkedIn format for processing
            linkedin_job_details = {
                'title': simplify_job.title,
                'company': simplify_job.company,
                'location': simplify_job.location,
                'description': f"Job from Simplify with {simplify_job.match_score:.1%} match",
                'salary': simplify_job.salary_range
            }
            
            # Enhanced analysis
            compatibility_score, analysis = matcher.analyze_job_compatibility(linkedin_job_details)
            
            if analysis.get('recommended_action') == 'apply':
                # Create application record with Simplify data
                application = linkedin_auto_apply.JobApplication(
                    company=simplify_job.company,
                    job_title=simplify_job.title,
                    location=simplify_job.location,
                    job_url=simplify_job.application_url,
                    application_status="Simplify Recommended",
                    applied_date=datetime.now().isoformat(),
                    job_description=f"Match Score: {simplify_job.match_score:.1%}",
                    requirements_match=str(analysis.get('requirements_match', {})),
                    salary_range=simplify_job.salary_range,
                    application_method="Simplify + LinkedIn",
                    notes=f"Simplify Score: {simplify_job.match_score:.1%}, Skills: {', '.join(simplify_job.skills_required[:3])}",
                    simplify_match=True,
                    simplify_score=simplify_job.match_score
                )
                
                enhanced_applications.append(application)
    
    logger.info(f"Simplify integration found {len(enhanced_applications)} high-quality matches")
    return enhanced_applications