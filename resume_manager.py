#!/usr/bin/env python3
"""
Resume Manager for LinkedIn Auto-Apply
Handles resume uploads, customization, and tracking
"""

import os
import logging
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
import time
from datetime import datetime
from pathlib import Path
import shutil
import hashlib
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

@dataclass
class ResumeVersion:
    file_path: str
    version_name: str
    target_role: str
    keywords: List[str]
    last_modified: str
    file_hash: str
    upload_count: int = 0

class ResumeManager:
    """Manages resume uploads and versions for job applications"""
    
    def __init__(self, resume_directory: str = "resumes"):
        self.resume_directory = Path(resume_directory)
        self.resume_directory.mkdir(exist_ok=True)
        
        self.versions = {}
        self.current_resume = None
        self.upload_history = []
        
        # Supply chain resume keywords for optimization
        self.supply_chain_keywords = {
            'operations': ['operations management', 'process improvement', 'lean manufacturing', 'operational excellence'],
            'logistics': ['logistics coordination', 'transportation', 'distribution', 'warehouse management'],
            'procurement': ['strategic sourcing', 'vendor management', 'cost reduction', 'supplier relations'],
            'planning': ['demand planning', 'supply planning', 'inventory optimization', 'forecasting'],
            'analytics': ['data analysis', 'supply chain analytics', 'KPI tracking', 'process metrics'],
            'technology': ['ERP systems', 'SAP', 'Excel', 'SQL', 'Python', 'Tableau'],
            'leadership': ['project management', 'cross-functional collaboration', 'team leadership', 'stakeholder management']
        }
        
        self.load_resume_versions()

    def load_resume_versions(self):
        """Load existing resume versions from directory"""
        try:
            versions_file = self.resume_directory / "versions.json"
            if versions_file.exists():
                with open(versions_file, 'r') as f:
                    data = json.load(f)
                    for version_data in data:
                        version = ResumeVersion(**version_data)
                        self.versions[version.version_name] = version
                        
            logger.info(f"Loaded {len(self.versions)} resume versions")
            
        except Exception as e:
            logger.error(f"Error loading resume versions: {e}")

    def save_resume_versions(self):
        """Save resume versions to file"""
        try:
            versions_file = self.resume_directory / "versions.json"
            versions_data = [
                {
                    'file_path': version.file_path,
                    'version_name': version.version_name,
                    'target_role': version.target_role,
                    'keywords': version.keywords,
                    'last_modified': version.last_modified,
                    'file_hash': version.file_hash,
                    'upload_count': version.upload_count
                }
                for version in self.versions.values()
            ]
            
            with open(versions_file, 'w') as f:
                json.dump(versions_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving resume versions: {e}")

    def add_resume_version(self, file_path: str, version_name: str, target_role: str, 
                          keywords: List[str] = None) -> bool:
        """Add a new resume version"""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                logger.error(f"Resume file not found: {file_path}")
                return False
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(source_path)
            
            # Copy to resume directory
            dest_path = self.resume_directory / f"{version_name}.pdf"
            shutil.copy2(source_path, dest_path)
            
            # Create version record
            version = ResumeVersion(
                file_path=str(dest_path),
                version_name=version_name,
                target_role=target_role,
                keywords=keywords or [],
                last_modified=datetime.now().isoformat(),
                file_hash=file_hash
            )
            
            self.versions[version_name] = version
            self.save_resume_versions()
            
            logger.info(f"Added resume version: {version_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding resume version: {e}")
            return False

    def select_best_resume(self, job_title: str, job_description: str) -> Optional[ResumeVersion]:
        """Select the best resume version for a specific job"""
        if not self.versions:
            logger.warning("No resume versions available")
            return None
        
        job_text = f"{job_title} {job_description}".lower()
        best_version = None
        best_score = 0
        
        for version in self.versions.values():
            score = self._calculate_resume_match_score(version, job_text)
            
            if score > best_score:
                best_score = score
                best_version = version
        
        if best_version:
            logger.info(f"Selected resume version '{best_version.version_name}' with score {best_score:.2f}")
        
        return best_version

    def _calculate_resume_match_score(self, version: ResumeVersion, job_text: str) -> float:
        """Calculate how well a resume version matches a job"""
        score = 0.0
        
        # Base score for target role match
        if version.target_role.lower() in job_text:
            score += 0.4
        
        # Keyword matching score
        if version.keywords:
            keyword_matches = sum(1 for keyword in version.keywords if keyword.lower() in job_text)
            keyword_score = (keyword_matches / len(version.keywords)) * 0.4
            score += keyword_score
        
        # Supply chain specific matching
        for category, keywords in self.supply_chain_keywords.items():
            category_matches = sum(1 for keyword in keywords if keyword.lower() in job_text)
            if category_matches > 0:
                score += 0.02 * category_matches  # Small bonus for each category match
        
        # Penalize overused resumes slightly
        if version.upload_count > 20:
            score *= 0.95
        
        return min(score, 1.0)

    def upload_resume_to_linkedin(self, driver, resume_version: ResumeVersion) -> bool:
        """Upload resume to LinkedIn during application process"""
        try:
            # Look for file upload input
            file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            
            resume_uploaded = False
            
            for file_input in file_inputs:
                try:
                    # Check if this is a resume upload field
                    parent = file_input.find_element(By.XPATH, "./ancestor::div[contains(@class, 'jobs-document-upload') or contains(@class, 'resume')]")
                    
                    if parent:
                        # Upload the resume
                        file_input.send_keys(resume_version.file_path)
                        time.sleep(2)
                        
                        # Wait for upload to complete
                        WebDriverWait(driver, 10).until(
                            lambda d: "uploaded" in d.page_source.lower() or 
                                     "attached" in d.page_source.lower()
                        )
                        
                        resume_uploaded = True
                        break
                        
                except Exception as e:
                    continue
            
            if resume_uploaded:
                # Update upload count
                resume_version.upload_count += 1
                self.save_resume_versions()
                
                logger.info(f"Successfully uploaded resume: {resume_version.version_name}")
                return True
            else:
                logger.warning("No resume upload field found")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading resume: {e}")
            return False

    def create_supply_chain_resume_versions(self, base_resume_path: str) -> bool:
        """Create specialized resume versions for different supply chain roles"""
        try:
            if not Path(base_resume_path).exists():
                logger.error(f"Base resume not found: {base_resume_path}")
                return False
            
            # Define specialized versions
            versions_to_create = [
                {
                    'name': 'supply_chain_operations',
                    'role': 'Operations Management',
                    'keywords': ['operations', 'process improvement', 'lean', 'efficiency', 'manufacturing', 'quality control']
                },
                {
                    'name': 'supply_chain_logistics',
                    'role': 'Logistics Coordination',
                    'keywords': ['logistics', 'transportation', 'distribution', 'warehouse', 'shipping', 'inventory']
                },
                {
                    'name': 'supply_chain_procurement',
                    'role': 'Procurement Specialist',
                    'keywords': ['procurement', 'sourcing', 'vendor management', 'cost reduction', 'supplier relations', 'negotiations']
                },
                {
                    'name': 'supply_chain_planning',
                    'role': 'Supply Planning Analyst',
                    'keywords': ['demand planning', 'supply planning', 'forecasting', 'inventory optimization', 'S&OP', 'analytics']
                },
                {
                    'name': 'supply_chain_rotational',
                    'role': 'Supply Chain Rotational Program',
                    'keywords': ['rotational program', 'leadership development', 'cross-functional', 'graduate program', 'management trainee']
                }
            ]
            
            for version_info in versions_to_create:
                success = self.add_resume_version(
                    file_path=base_resume_path,
                    version_name=version_info['name'],
                    target_role=version_info['role'],
                    keywords=version_info['keywords']
                )
                
                if success:
                    logger.info(f"Created specialized resume: {version_info['name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating resume versions: {e}")
            return False

    def get_resume_usage_stats(self) -> Dict:
        """Get statistics about resume usage"""
        if not self.versions:
            return {}
        
        stats = {
            'total_versions': len(self.versions),
            'total_uploads': sum(v.upload_count for v in self.versions.values()),
            'most_used_version': None,
            'least_used_version': None,
            'versions_by_role': {}
        }
        
        # Find most and least used
        most_used = max(self.versions.values(), key=lambda v: v.upload_count)
        least_used = min(self.versions.values(), key=lambda v: v.upload_count)
        
        stats['most_used_version'] = {
            'name': most_used.version_name,
            'uploads': most_used.upload_count,
            'role': most_used.target_role
        }
        
        stats['least_used_version'] = {
            'name': least_used.version_name,
            'uploads': least_used.upload_count,
            'role': least_used.target_role
        }
        
        # Group by role
        for version in self.versions.values():
            role = version.target_role
            if role not in stats['versions_by_role']:
                stats['versions_by_role'][role] = []
            stats['versions_by_role'][role].append({
                'name': version.version_name,
                'uploads': version.upload_count
            })
        
        return stats

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def optimize_resume_selection(self, recent_applications: List[Dict]) -> Dict:
        """Analyze recent applications to optimize resume selection"""
        try:
            analysis = {
                'success_rate_by_version': {},
                'recommendations': []
            }
            
            # Analyze success rates by resume version
            version_stats = {}
            for app in recent_applications:
                resume_used = app.get('resume_version', 'unknown')
                status = app.get('application_status', '')
                
                if resume_used not in version_stats:
                    version_stats[resume_used] = {'total': 0, 'successful': 0}
                
                version_stats[resume_used]['total'] += 1
                if status in ['Applied', 'Interview', 'Offer']:
                    version_stats[resume_used]['successful'] += 1
            
            # Calculate success rates
            for version, stats in version_stats.items():
                if stats['total'] > 0:
                    success_rate = stats['successful'] / stats['total']
                    analysis['success_rate_by_version'][version] = {
                        'success_rate': success_rate,
                        'total_applications': stats['total'],
                        'successful_applications': stats['successful']
                    }
            
            # Generate recommendations
            if analysis['success_rate_by_version']:
                best_version = max(analysis['success_rate_by_version'].items(), 
                                 key=lambda x: x[1]['success_rate'])
                
                analysis['recommendations'].append(
                    f"Resume version '{best_version[0]}' has the highest success rate at {best_version[1]['success_rate']:.1%}"
                )
                
                # Find underperforming versions
                avg_success_rate = sum(v['success_rate'] for v in analysis['success_rate_by_version'].values()) / len(analysis['success_rate_by_version'])
                
                for version, stats in analysis['success_rate_by_version'].items():
                    if stats['success_rate'] < avg_success_rate * 0.7 and stats['total_applications'] > 5:
                        analysis['recommendations'].append(
                            f"Consider updating resume version '{version}' - success rate {stats['success_rate']:.1%} is below average"
                        )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error optimizing resume selection: {e}")
            return {}

    def backup_resumes(self, backup_directory: str = "resume_backups") -> bool:
        """Create backup of all resume versions"""
        try:
            backup_path = Path(backup_directory)
            backup_path.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_folder = backup_path / f"backup_{timestamp}"
            backup_folder.mkdir()
            
            # Copy all resume files
            for version in self.versions.values():
                source_file = Path(version.file_path)
                if source_file.exists():
                    dest_file = backup_folder / source_file.name
                    shutil.copy2(source_file, dest_file)
            
            # Copy versions metadata
            versions_backup = backup_folder / "versions.json"
            shutil.copy2(self.resume_directory / "versions.json", versions_backup)
            
            logger.info(f"Resume backup created: {backup_folder}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating resume backup: {e}")
            return False

class CoverLetterGenerator:
    """Generate customized cover letters for applications"""
    
    def __init__(self):
        self.templates = {
            'operations': """
Dear Hiring Manager,

I am excited to apply for the {job_title} position at {company}. With my background in operations and process improvement, I am eager to contribute to your supply chain excellence.

My experience includes {relevant_experience}, which aligns well with your requirements for {key_requirements}. I am particularly drawn to {company}'s commitment to operational excellence and innovation.

I would welcome the opportunity to discuss how my skills in {key_skills} can contribute to your team's success.

Best regards,
[Your Name]
            """,
            
            'logistics': """
Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} role at {company}. My passion for logistics and supply chain optimization makes me an ideal candidate for this position.

Through my experience in {relevant_experience}, I have developed expertise in {key_skills} that directly applies to your needs. I am impressed by {company}'s innovative approach to logistics management.

I look forward to the opportunity to contribute to your logistics operations and drive continuous improvement.

Sincerely,
[Your Name]
            """,
            
            'rotational': """
Dear Hiring Manager,

I am thrilled to apply for the {job_title} at {company}. As a recent graduate seeking to launch my career in supply chain management, I am particularly excited about the comprehensive learning opportunities this rotational program offers.

My academic background and internship experience in {relevant_experience} have prepared me for the challenges of a dynamic, cross-functional role. I am eager to contribute fresh perspectives while learning from your experienced team.

The opportunity to rotate through different functions at {company} aligns perfectly with my career goals and commitment to becoming a well-rounded supply chain professional.

Best regards,
[Your Name]
            """
        }

    def generate_cover_letter(self, job_title: str, company: str, job_description: str, 
                            user_profile: Dict = None) -> str:
        """Generate a customized cover letter"""
        try:
            # Determine the best template
            template_type = self._select_template(job_title, job_description)
            template = self.templates.get(template_type, self.templates['operations'])
            
            # Extract key information
            key_requirements = self._extract_key_requirements(job_description)
            key_skills = self._extract_key_skills(job_description, user_profile)
            relevant_experience = self._get_relevant_experience(user_profile)
            
            # Fill template
            cover_letter = template.format(
                job_title=job_title,
                company=company,
                key_requirements=key_requirements,
                key_skills=key_skills,
                relevant_experience=relevant_experience
            ).strip()
            
            return cover_letter
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return "I am excited to apply for this position and contribute to your team's success."

    def _select_template(self, job_title: str, job_description: str) -> str:
        """Select the most appropriate template"""
        text = f"{job_title} {job_description}".lower()
        
        if 'rotational' in text or 'leadership development' in text:
            return 'rotational'
        elif 'logistics' in text or 'transportation' in text:
            return 'logistics'
        else:
            return 'operations'

    def _extract_key_requirements(self, job_description: str) -> str:
        """Extract key requirements from job description"""
        # Simple extraction - in practice, this could be more sophisticated
        key_phrases = [
            'process improvement', 'data analysis', 'project management',
            'cross-functional collaboration', 'supply chain optimization',
            'inventory management', 'vendor management'
        ]
        
        found_requirements = []
        job_desc_lower = job_description.lower()
        
        for phrase in key_phrases:
            if phrase in job_desc_lower:
                found_requirements.append(phrase)
        
        return ', '.join(found_requirements[:3]) if found_requirements else 'operational excellence'

    def _extract_key_skills(self, job_description: str, user_profile: Dict = None) -> str:
        """Extract relevant skills to highlight"""
        skills = ['analytical thinking', 'problem solving', 'communication']
        
        if user_profile and 'skills' in user_profile:
            user_skills = [skill.lower() for skill in user_profile['skills']]
            job_desc_lower = job_description.lower()
            
            relevant_skills = []
            for skill in user_skills:
                if skill in job_desc_lower:
                    relevant_skills.append(skill)
            
            if relevant_skills:
                skills = relevant_skills[:3]
        
        return ', '.join(skills)

    def _get_relevant_experience(self, user_profile: Dict = None) -> str:
        """Get relevant experience description"""
        if user_profile and 'experience' in user_profile:
            return user_profile['experience'][:100] + "..."
        else:
            return "academic projects and internship experience"