import asyncio
import time
import random
import hashlib
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import re
from urllib.parse import urlencode, quote
from dataclasses import dataclass
import logging

try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    from fake_useragent import UserAgent
except ImportError:
    class UserAgent:
        @property
        def random(self):
            return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

try:
    import polars as pl
except ImportError:
    pl = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class JobListing:
    """Optimized job listing data structure."""
    job_title: str
    company_name: str
    location: str
    job_link: str
    work_type: str = "N/A"
    salary: str = "N/A"
    description: str = ""
    posted_date: str = "N/A"
    source: str = ""

class AsyncJobScraper:
    """Async job scraper for maximum performance."""
    
    def __init__(self):
        self.ua = UserAgent()
        self.session = None
        self.rate_limits = {
            'linkedin': 0.5,  # 2 requests per second
            'indeed': 0.3,   # 3 requests per second
            'glassdoor': 0.7  # 1.4 requests per second
        }
        
    async def create_session(self):
        """Create optimized aiohttp session."""
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=20,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={'User-Agent': self.ua.random}
        )
    
    async def close_session(self):
        """Close aiohttp session."""
        if self.session:
            await self.session.close()
    
    def _extract_salary(self, text: str) -> str:
        """Extract salary information with regex patterns."""
        if not text:
            return "N/A"
        
        # Common salary patterns
        salary_patterns = [
            r'\$[\d,]+(?:\.\d{2})?\s*-\s*\$[\d,]+(?:\.\d{2})?(?:\s*(?:per year|annually|\/year))?',
            r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:per year|annually|\/year|k))',
            r'[\d,]+\s*-\s*[\d,]+\s*(?:USD|dollars?)',
            r'[\d,]+k?\s*-\s*[\d,]+k?',
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        return "N/A"
    
    def _extract_work_type(self, text: str) -> str:
        """Extract work type information."""
        if not text:
            return "N/A"
        
        text_lower = text.lower()
        
        # Work type patterns
        if any(term in text_lower for term in ['remote', 'work from home', 'telecommute']):
            return "Remote"
        elif any(term in text_lower for term in ['hybrid', 'mixed']):
            return "Hybrid"
        elif any(term in text_lower for term in ['on-site', 'onsite', 'office']):
            return "On-site"
        elif any(term in text_lower for term in ['part-time', 'part time']):
            return "Part-time"
        elif any(term in text_lower for term in ['full-time', 'full time']):
            return "Full-time"
        elif any(term in text_lower for term in ['contract', 'contractor']):
            return "Contract"
        elif any(term in text_lower for term in ['internship', 'intern']):
            return "Internship"
        
        return "Full-time"  # Default assumption
    
    async def scrape_linkedin_jobs(self, company: str, role: str, location: str, limit: int = 50) -> List[JobListing]:
        """Scrape LinkedIn jobs with optimized selectors."""
        jobs = []
        try:
            # LinkedIn job search URL
            params = {
                'keywords': f"{role} {company}",
                'location': location,
                'f_TPR': 'r604800',  # Past week
                'f_E': '2,3,4',      # Entry level to senior
                'start': 0
            }
            
            url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?{urlencode(params)}"
            
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Referer': 'https://www.linkedin.com/',
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Optimized selectors
                    job_cards = soup.find_all('div', class_='job-search-card')
                    
                    for card in job_cards[:limit]:
                        try:
                            # Extract job information
                            title_elem = card.find('h3', class_='base-search-card__title')
                            title = title_elem.get_text(strip=True) if title_elem else "N/A"
                            
                            company_elem = card.find('h4', class_='base-search-card__subtitle')
                            company = company_elem.get_text(strip=True) if company_elem else "N/A"
                            
                            location_elem = card.find('span', class_='job-search-card__location')
                            job_location = location_elem.get_text(strip=True) if location_elem else "N/A"
                            
                            link_elem = card.find('a', class_='base-card__full-link')
                            link = link_elem.get('href', '') if link_elem else "N/A"
                            
                            # Extract additional metadata
                            metadata_text = card.get_text()
                            work_type = self._extract_work_type(metadata_text)
                            salary = self._extract_salary(metadata_text)
                            
                            jobs.append(JobListing(
                                job_title=title,
                                company_name=company,
                                location=job_location,
                                job_link=link,
                                work_type=work_type,
                                salary=salary,
                                source="LinkedIn"
                            ))
                            
                        except Exception as e:
                            logger.debug(f"Error parsing LinkedIn job card: {e}")
                            continue
            
            await asyncio.sleep(self.rate_limits['linkedin'])
            
        except Exception as e:
            logger.error(f"LinkedIn scraping error: {e}")
        
        return jobs
    
    async def scrape_indeed_jobs(self, company: str, role: str, location: str, limit: int = 50) -> List[JobListing]:
        """Scrape Indeed jobs with optimized performance."""
        jobs = []
        try:
            # Indeed search parameters
            params = {
                'q': f"{role} {company}",
                'l': location,
                'fromage': 7,  # Past week
                'limit': limit,
                'start': 0
            }
            
            url = f"https://www.indeed.com/jobs?{urlencode(params)}"
            
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.indeed.com/',
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Indeed job cards
                    job_cards = soup.find_all('div', class_='job_seen_beacon')
                    
                    for card in job_cards[:limit]:
                        try:
                            # Title and link
                            title_elem = card.find('h2', class_='jobTitle')
                            if title_elem:
                                link_elem = title_elem.find('a')
                                title = link_elem.get_text(strip=True) if link_elem else "N/A"
                                link = f"https://www.indeed.com{link_elem.get('href', '')}" if link_elem else "N/A"
                            else:
                                title = "N/A"
                                link = "N/A"
                            
                            # Company
                            company_elem = card.find('span', class_='companyName')
                            company = company_elem.get_text(strip=True) if company_elem else "N/A"
                            
                            # Location
                            location_elem = card.find('div', class_='companyLocation')
                            job_location = location_elem.get_text(strip=True) if location_elem else "N/A"
                            
                            # Salary
                            salary_elem = card.find('span', class_='salaryText')
                            salary = salary_elem.get_text(strip=True) if salary_elem else "N/A"
                            
                            # Work type from metadata
                            metadata_text = card.get_text()
                            work_type = self._extract_work_type(metadata_text)
                            
                            jobs.append(JobListing(
                                job_title=title,
                                company_name=company,
                                location=job_location,
                                job_link=link,
                                work_type=work_type,
                                salary=salary,
                                source="Indeed"
                            ))
                            
                        except Exception as e:
                            logger.debug(f"Error parsing Indeed job card: {e}")
                            continue
            
            await asyncio.sleep(self.rate_limits['indeed'])
            
        except Exception as e:
            logger.error(f"Indeed scraping error: {e}")
        
        return jobs
    
    async def scrape_glassdoor_jobs(self, company: str, role: str, location: str, limit: int = 50) -> List[JobListing]:
        """Scrape Glassdoor jobs."""
        jobs = []
        try:
            # Glassdoor search (simplified approach)
            params = {
                'sc.keyword': f"{role} {company}",
                'locT': 'C',
                'locId': location,
                'jobType': '',
                'fromAge': 7,
                'minSalary': 0,
                'includeNoSalaryJobs': 'true'
            }
            
            url = f"https://www.glassdoor.com/Job/jobs.htm?{urlencode(params)}"
            
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.glassdoor.com/',
            }
            
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'lxml')
                    
                    # Glassdoor job listings
                    job_cards = soup.find_all('li', class_='react-job-listing')
                    
                    for card in job_cards[:limit]:
                        try:
                            # Title and link
                            title_elem = card.find('a', {'data-test': 'job-title'})
                            title = title_elem.get_text(strip=True) if title_elem else "N/A"
                            link = f"https://www.glassdoor.com{title_elem.get('href', '')}" if title_elem else "N/A"
                            
                            # Company
                            company_elem = card.find('span', {'data-test': 'employer-name'})
                            company = company_elem.get_text(strip=True) if company_elem else "N/A"
                            
                            # Location
                            location_elem = card.find('span', {'data-test': 'job-location'})
                            job_location = location_elem.get_text(strip=True) if location_elem else "N/A"
                            
                            # Salary
                            salary_elem = card.find('span', {'data-test': 'detailSalary'})
                            salary = salary_elem.get_text(strip=True) if salary_elem else "N/A"
                            
                            # Work type
                            metadata_text = card.get_text()
                            work_type = self._extract_work_type(metadata_text)
                            
                            jobs.append(JobListing(
                                job_title=title,
                                company_name=company,
                                location=job_location,
                                job_link=link,
                                work_type=work_type,
                                salary=salary,
                                source="Glassdoor"
                            ))
                            
                        except Exception as e:
                            logger.debug(f"Error parsing Glassdoor job card: {e}")
                            continue
            
            await asyncio.sleep(self.rate_limits['glassdoor'])
            
        except Exception as e:
            logger.error(f"Glassdoor scraping error: {e}")
        
        return jobs


class JobScraperManager:
    """High-performance job scraper manager with parallel processing."""
    
    def __init__(self):
        self.scraper = AsyncJobScraper()
        self.executor = ThreadPoolExecutor(max_workers=6)
        self.background_tasks = set()
        
    def initialize(self):
        """Initialize the scraper manager."""
        logger.info("Job scraper manager initialized")
        
    async def scrape_all_platforms(self, company: str, role: str, location: str, limit_per_platform: int = 50) -> List[JobListing]:
        """Scrape all platforms concurrently for maximum speed."""
        await self.scraper.create_session()
        
        try:
            # Run all scrapers concurrently
            tasks = [
                self.scraper.scrape_linkedin_jobs(company, role, location, limit_per_platform),
                self.scraper.scrape_indeed_jobs(company, role, location, limit_per_platform),
                self.scraper.scrape_glassdoor_jobs(company, role, location, limit_per_platform)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            all_jobs = []
            for result in results:
                if isinstance(result, list):
                    all_jobs.extend(result)
                else:
                    logger.error(f"Scraper error: {result}")
            
            # Remove duplicates based on job title + company
            seen = set()
            unique_jobs = []
            for job in all_jobs:
                job_key = f"{job.job_title.lower()}:{job.company_name.lower()}"
                if job_key not in seen:
                    seen.add(job_key)
                    unique_jobs.append(job)
            
            return unique_jobs
            
        finally:
            await self.scraper.close_session()
    
    def trigger_background_scrape(self, params: Dict):
        """Trigger background scraping for future cache population."""
        task = asyncio.create_task(self._background_scrape_task(params))
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
    
    async def _background_scrape_task(self, params: Dict):
        """Background scraping task to populate cache."""
        try:
            companies = params.get('companies', [])
            roles = params.get('roles', [])
            locations = params.get('locations', [])
            
            # Scrape for each combination
            for company in companies:
                for role in roles:
                    for location in locations:
                        if company.get('company') != 'any' and role.get('role') != 'any' and location.get('location') != 'any':
                            jobs = await self.scrape_all_platforms(
                                company['company'], 
                                role['role'], 
                                location['location'],
                                limit_per_platform=30
                            )
                            
                            if jobs:
                                # Convert to dict format for caching
                                jobs_dict = [
                                    {
                                        'job_title': job.job_title,
                                        'company_name': job.company_name,
                                        'location': job.location,
                                        'job_link': job.job_link,
                                        'work_type': job.work_type,
                                        'salary': job.salary,
                                        'source': job.source
                                    }
                                    for job in jobs
                                ]
                                
                                # Cache the results (would need cache manager instance)
                                logger.info(f"Background scraped {len(jobs)} jobs for {company['company']} {role['role']} in {location['location']}")
            
        except Exception as e:
            logger.error(f"Background scraping error: {e}")
    
    def get_cached_or_fresh_jobs(self, cache_manager, params: Dict) -> List[Dict]:
        """Get jobs from cache or scrape fresh ones."""
        # This would integrate with the cache manager
        # For now, return empty list to trigger database fallback
        return []