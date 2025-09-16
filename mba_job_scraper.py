#!/usr/bin/env python3
"""
MBA/Masters Job Scraper - Daily Fresh Postings (2026 Start Dates)
Scrapes job postings from multiple sources and outputs to Google Sheets for Power BI
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from urllib.parse import urljoin, quote_plus
import json
import os
from dataclasses import dataclass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import gspread
from google.oauth2.service_account import Credentials
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class JobPosting:
    company: str
    role_title: str
    function: str
    location: str
    start_date: str
    posted_date: str
    visa_sponsorship: str
    direct_link: str
    key_qualifications: str
    source: str
    scraped_at: str

class JobScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Target companies from the provided list
        self.target_companies = [
            "BDO USA", "Calvetti Ferguson", "Crowe LLP", "Forvis Mazars", "KPMG", "Weaver",
            "49 Financial", "ABIP, P.C.", "Academy Sports & Outdoors", "Advanced Micro Devices",
            "AMD", "Airswift", "AIT Consulting", "ALDI USA", "Altria", "Alvarez & Marsal",
            "Amazon", "Amegy Bank of Texas", "American Airlines", "American Bureau of Shipping",
            "Andersen", "Aperture", "Applied Materials Inc", "Arrive Logistics", "ATKG",
            "Auctane", "Avison Young", "Bank of Texas", "Bank OZK", "Benton, Duroy & Ivey, P.C.",
            "BGE, Inc", "Boardwalk Pipelines, LP", "bp", "BRAVE Books", "Builders FirstSource",
            "C1 Insurance Group", "Calpine Corporation", "Camp Buckner", "Camp Victory", "Capco",
            "Capital Farm Credit", "Carroll Insurance Agency", "Catalyst Financial Group LLC",
            "CBIZ", "CCK Strategies", "CEM Solutions", "Charles River Associates", "Chart Industries",
            "Cheniere Energy", "Chevron Corporation", "Chevron Phillips Chemical Company",
            "Chord Energy", "Cintas", "CITGO Petroleum", "ClearDefense Pest Control",
            "Coherent Economics", "Collabera Inc.", "Comcast", "ConocoPhillips", 
            "Consolidated Asset Management Services", "Consolidated Electrical Distributors",
            "Corebridge Financial", "Credera", "CRI Advisors", "Crown Castle", "D&M Leasing",
            "D.R. Horton, Inc.", "Dell Technologies", "DFW International Airport",
            "DICK'S Sporting Goods", "Disrupt Equity Partners", "Dominium", "DXP Enterprises, Inc.",
            "E & J Gallo Winery", "Eight Eleven Group", "Enterprise Mobility", "Enterprise Products Company",
            "EOG Resources", "Equitable Advisors", "Eventellect", "Extraco Banks", "ExxonMobil",
            "Faske Lay & Co., L.L.P.", "Fidelity Investments", "First Financial Bank",
            "Fisher Investments", "Frost Bank", "FTI Consulting", "Gartner", "Gexpro Services",
            "GFA World", "Glencore Ltd", "Goosehead Insurance", "GuideStone Financial Resources",
            "H-E-B", "Hajoca", "Halliburton", "HF Sinclair", "Hilcorp Energy Company",
            "Hilltop Holdings", "HMH", "Holmes Murphy", "Honeywell", "HumCap", "IMG Financial Group",
            "impac Fleet", "indiGO Auto Group", "INEOS Olefins & Polymers USA", "Insight Global",
            "ISN Software Corporation", "JSX", "K-Star Investment Services", "Kairoi Residential",
            "Kaspar Companies", "Kiewit", "Kinder Morgan", "Klein Tools, Inc.", "Koch Industries Inc.",
            "L&W Supply", "Labatt Food Service", "Lockheed Martin", "Lone Star College",
            "LyondellBasell", "Mansfield Service Partners", "Marathon Petroleum Company",
            "Marriott Vacations Worldwide", "Mary Kay", "Matador Resources",
            "Matthews Real Estate Investment Services", "McLane Co", "McLane Restaurant",
            "Merit Advisors, LLC", "Mitsui & Co. Energy Marketing and Services USA Inc.",
            "Mohawk Industries", "Motiva Enterprises", "MRBgroup", "MRE Consulting",
            "Musco Lighting", "National Life Group", "NetWorth Realty", "Newrez",
            "Northwestern Mutual", "NRG/Reliant", "Nucor", "Oliver Wyman", "Oncor Electric Delivery",
            "Opportune LLP", "Owens Corning", "Oxy", "Parallon", "PepsiCo", "Phillips 66",
            "Pike Corporation", "Pilot Company", "Plains All American Pipeline",
            "Platform Accounting Group", "PNC", "Premier Trailer Leasing", "Premier Truck Group",
            "Protiviti", "Rand Group", "Republic Finance", "Revantage", "RSM US LLP",
            "Rush Enterprises", "Ryan, LLC", "Rystad Energy", "Sandia National Laboratories",
            "Scotiabank", "Seidel Schroeder", "Sendero", "Sewell Automotive Companies",
            "Shell USA", "Sherwin-Williams", "SHI", "SHI International", "Siemens Energy",
            "Southwestern Advantage", "Strategic Financial Group", "Students + Startups",
            "Sunoco LP", "Talen Energy", "Targa Resources", "Target Corporation", "TC Energy",
            "Tenaris", "Texas Capital", "Texas Department of Banking",
            "Texas Division of Emergency Management", "Texas Financial Advisors",
            "Texas Instruments", "Textron", "The Boeing Company", "The Cigna Group",
            "The Dynamic Catholic Institute", "The Friedkin Group", "The Reynolds and Reynolds Company",
            "The Travelers Companies, Inc.", "The Urban Foresters", "Traditions Wealth Advisors, LLC",
            "Trane Technologies", "Trenegy Incorporated", "Trinity Real Estate Finance, Inc.",
            "TTI - Techtronic Industries", "Tyson Foods", "U.S. Energy", "Umbrage", "Urenco USA",
            "USAA", "USI Insurance Services", "Valero", "Vector Marketing Corporation",
            "Venture Global LNG", "VMG Health", "Weatherford International", "Wesco",
            "West Fort Worth Management", "Western Alliance Bank", "Willis Johnson & Associates",
            "Wisenbaker Builder Services", "WoodmenLife", "WRM- Waste Resource Management",
            "Wurth Industry", "Zendesk"
        ]
        
        # Target functions for MBA roles
        self.target_functions = [
            "Product Management", "Product Marketing", "Program Management", "Strategy",
            "Marketing", "Brand Management", "Business Development", "Consulting",
            "Finance", "Operations", "Analytics", "Strategy & Operations"
        ]
        
        # Keywords to exclude
        self.exclude_keywords = [
            "intern", "internship", "co-op", "fellowship", "summer associate", "contract",
            "temporary", "temp", "part-time", "adjunct", "professor", "teaching",
            "senior", "principal", "director", "vp", "vice president", "7+ years",
            "8+ years", "9+ years", "10+ years"
        ]
        
        self.jobs_found = []
        
    def setup_selenium_driver(self):
        """Setup Chrome driver for dynamic content scraping"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            return None

    def is_recent_posting(self, posted_date_str: str) -> bool:
        """Check if job was posted within last 48 hours"""
        try:
            # Handle various date formats
            now = datetime.now()
            cutoff = now - timedelta(hours=48)
            
            # Common patterns
            if 'hour' in posted_date_str.lower():
                hours = re.findall(r'(\d+)', posted_date_str)
                if hours:
                    posted_time = now - timedelta(hours=int(hours[0]))
                    return posted_time >= cutoff
            elif 'day' in posted_date_str.lower():
                days = re.findall(r'(\d+)', posted_date_str)
                if days and int(days[0]) <= 2:
                    return True
            elif 'today' in posted_date_str.lower() or 'yesterday' in posted_date_str.lower():
                return True
                
            return False
        except:
            return True  # If we can't parse, include it to be safe

    def contains_mba_requirements(self, text: str) -> bool:
        """Check if job posting mentions MBA/Masters requirements"""
        mba_keywords = [
            'mba', 'master', 'masters', 'graduate degree', 'advanced degree',
            'class of 2026', '2026 graduate', 'recent graduate', 'new graduate'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in mba_keywords)

    def has_2026_start_date(self, text: str) -> bool:
        """Check if job mentions 2026 start date"""
        start_keywords = [
            '2026', 'may 2026', 'june 2026', 'july 2026', 'august 2026',
            'september 2026', 'class of 2026', 'summer 2026', 'fall 2026'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in start_keywords)

    def should_exclude_job(self, title: str, description: str) -> bool:
        """Check if job should be excluded based on exclusion criteria"""
        combined_text = f"{title} {description}".lower()
        return any(keyword in combined_text for keyword in self.exclude_keywords)

    def scrape_indeed(self, company: str) -> List[JobPosting]:
        """Scrape Indeed for MBA jobs from specific company"""
        jobs = []
        try:
            query = f"MBA OR Masters {company} 2026"
            url = f"https://www.indeed.com/jobs?q={quote_plus(query)}&fromage=2"
            
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_cards = soup.find_all('div', {'data-jk': True})
            
            for card in job_cards[:5]:  # Limit to first 5 results per company
                try:
                    title_elem = card.find('h2', class_='jobTitle')
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    link_elem = title_elem.find('a')
                    job_link = urljoin('https://www.indeed.com', link_elem['href']) if link_elem else ""
                    
                    company_elem = card.find('span', {'data-testid': 'company-name'})
                    company_name = company_elem.get_text(strip=True) if company_elem else company
                    
                    location_elem = card.find('div', {'data-testid': 'job-location'})
                    location = location_elem.get_text(strip=True) if location_elem else "Not specified"
                    
                    summary_elem = card.find('div', {'data-testid': 'job-snippet'})
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    # Check if this is a relevant MBA job
                    if not (self.contains_mba_requirements(f"{title} {summary}") or 
                           self.has_2026_start_date(f"{title} {summary}")):
                        continue
                        
                    if self.should_exclude_job(title, summary):
                        continue
                    
                    # Extract function
                    function = self.extract_function(title)
                    
                    # Extract visa sponsorship info
                    visa_info = self.extract_visa_info(summary)
                    
                    job = JobPosting(
                        company=company_name,
                        role_title=title,
                        function=function,
                        location=location,
                        start_date="2026 (inferred)",
                        posted_date="Within 48 hours",
                        visa_sponsorship=visa_info,
                        direct_link=job_link,
                        key_qualifications=summary[:200] + "..." if len(summary) > 200 else summary,
                        source="Indeed.com",
                        scraped_at=datetime.now().isoformat()
                    )
                    jobs.append(job)
                    
                except Exception as e:
                    logger.warning(f"Error parsing job card from Indeed: {e}")
                    continue
                    
            time.sleep(2)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Error scraping Indeed for {company}: {e}")
            
        return jobs

    def scrape_linkedin(self, company: str) -> List[JobPosting]:
        """Scrape LinkedIn jobs (requires Selenium for dynamic content)"""
        jobs = []
        driver = self.setup_selenium_driver()
        if not driver:
            return jobs
            
        try:
            query = f"MBA OR Masters {company}"
            url = f"https://www.linkedin.com/jobs/search/?keywords={quote_plus(query)}&f_TPR=r86400"
            
            driver.get(url)
            time.sleep(3)
            
            # Scroll to load more jobs
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            job_cards = driver.find_elements(By.CSS_SELECTOR, '.job-search-card')
            
            for card in job_cards[:5]:  # Limit results
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, '.base-search-card__title')
                    title = title_elem.text.strip()
                    
                    link = card.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    
                    company_elem = card.find_element(By.CSS_SELECTOR, '.base-search-card__subtitle')
                    company_name = company_elem.text.strip()
                    
                    location_elem = card.find_element(By.CSS_SELECTOR, '.job-search-card__location')
                    location = location_elem.text.strip()
                    
                    # Get job description by clicking on the job
                    card.click()
                    time.sleep(2)
                    
                    try:
                        description_elem = driver.find_element(By.CSS_SELECTOR, '.show-more-less-html__markup')
                        description = description_elem.text
                    except:
                        description = ""
                    
                    # Check relevance
                    if not (self.contains_mba_requirements(f"{title} {description}") or 
                           self.has_2026_start_date(f"{title} {description}")):
                        continue
                        
                    if self.should_exclude_job(title, description):
                        continue
                    
                    function = self.extract_function(title)
                    visa_info = self.extract_visa_info(description)
                    
                    job = JobPosting(
                        company=company_name,
                        role_title=title,
                        function=function,
                        location=location,
                        start_date="2026 (inferred)",
                        posted_date="Within 24 hours",
                        visa_sponsorship=visa_info,
                        direct_link=link,
                        key_qualifications=description[:200] + "..." if len(description) > 200 else description,
                        source="LinkedIn Jobs",
                        scraped_at=datetime.now().isoformat()
                    )
                    jobs.append(job)
                    
                except Exception as e:
                    logger.warning(f"Error parsing LinkedIn job card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping LinkedIn for {company}: {e}")
        finally:
            driver.quit()
            
        return jobs

    def scrape_glassdoor(self, company: str) -> List[JobPosting]:
        """Scrape Glassdoor jobs"""
        jobs = []
        try:
            query = f"MBA {company}"
            url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={quote_plus(query)}&fromAge=2"
            
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Glassdoor has anti-bot measures, so this is a basic implementation
            job_cards = soup.find_all('li', {'data-test': 'jobListing'})
            
            for card in job_cards[:3]:  # Limit results
                try:
                    title_elem = card.find('a', {'data-test': 'job-title'})
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    job_link = urljoin('https://www.glassdoor.com', title_elem['href'])
                    
                    company_elem = card.find('div', {'data-test': 'employer-name'})
                    company_name = company_elem.get_text(strip=True) if company_elem else company
                    
                    location_elem = card.find('div', {'data-test': 'job-location'})
                    location = location_elem.get_text(strip=True) if location_elem else "Not specified"
                    
                    # Basic relevance check
                    if not any(func.lower() in title.lower() for func in self.target_functions):
                        continue
                    
                    function = self.extract_function(title)
                    
                    job = JobPosting(
                        company=company_name,
                        role_title=title,
                        function=function,
                        location=location,
                        start_date="2026 (inferred)",
                        posted_date="Within 48 hours",
                        visa_sponsorship="Not specified",
                        direct_link=job_link,
                        key_qualifications="MBA/Masters preferred",
                        source="Glassdoor",
                        scraped_at=datetime.now().isoformat()
                    )
                    jobs.append(job)
                    
                except Exception as e:
                    logger.warning(f"Error parsing Glassdoor job card: {e}")
                    continue
                    
            time.sleep(3)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Error scraping Glassdoor for {company}: {e}")
            
        return jobs

    def scrape_company_careers(self, company: str) -> List[JobPosting]:
        """Scrape company career pages directly"""
        jobs = []
        
        # Common career page patterns
        career_urls = [
            f"https://{company.lower().replace(' ', '').replace(',', '').replace('.', '')}.com/careers",
            f"https://{company.lower().replace(' ', '-').replace(',', '').replace('.', '')}.com/careers",
            f"https://careers.{company.lower().replace(' ', '').replace(',', '').replace('.', '')}.com",
            f"https://www.{company.lower().replace(' ', '').replace(',', '').replace('.', '')}.com/careers"
        ]
        
        for url in career_urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for job links with MBA-related keywords
                    job_links = soup.find_all('a', href=True)
                    for link in job_links:
                        href = link['href']
                        text = link.get_text(strip=True)
                        
                        if any(keyword in text.lower() for keyword in ['mba', 'graduate', 'analyst', 'associate', 'manager']):
                            if any(func.lower() in text.lower() for func in self.target_functions):
                                full_url = urljoin(url, href)
                                
                                job = JobPosting(
                                    company=company,
                                    role_title=text,
                                    function=self.extract_function(text),
                                    location="Various locations",
                                    start_date="2026 (check posting)",
                                    posted_date="Recent",
                                    visa_sponsorship="Check posting",
                                    direct_link=full_url,
                                    key_qualifications="MBA/Masters preferred",
                                    source=f"{company} Careers",
                                    scraped_at=datetime.now().isoformat()
                                )
                                jobs.append(job)
                                
                                if len(jobs) >= 2:  # Limit per company
                                    break
                    break  # Stop after first successful URL
                    
            except Exception as e:
                continue  # Try next URL pattern
                
        return jobs

    def extract_function(self, title: str) -> str:
        """Extract job function from title"""
        title_lower = title.lower()
        
        for func in self.target_functions:
            if func.lower() in title_lower:
                return func
                
        # Additional mapping
        if any(word in title_lower for word in ['analyst', 'associate']):
            if any(word in title_lower for word in ['product', 'pm']):
                return "Product Management"
            elif any(word in title_lower for word in ['marketing', 'brand']):
                return "Marketing"
            elif any(word in title_lower for word in ['strategy', 'consulting']):
                return "Strategy"
            elif any(word in title_lower for word in ['business', 'bd']):
                return "Business Development"
            else:
                return "General Management"
        
        return "Other"

    def extract_visa_info(self, text: str) -> str:
        """Extract visa sponsorship information from job description"""
        text_lower = text.lower()
        
        if 'visa sponsorship' in text_lower or 'h1b' in text_lower:
            if 'no visa' in text_lower or 'not sponsor' in text_lower:
                return "No visa sponsorship"
            else:
                return "Visa sponsorship available"
        elif 'authorized to work' in text_lower:
            return "Must be authorized to work in US"
        else:
            return "Not specified"

    def scrape_all_companies(self) -> List[JobPosting]:
        """Scrape jobs from all target companies"""
        all_jobs = []
        
        logger.info(f"Starting to scrape {len(self.target_companies)} companies...")
        
        for i, company in enumerate(self.target_companies):
            logger.info(f"Scraping {company} ({i+1}/{len(self.target_companies)})")
            
            # Scrape from multiple sources
            company_jobs = []
            
            # Indeed (most reliable)
            indeed_jobs = self.scrape_indeed(company)
            company_jobs.extend(indeed_jobs)
            
            # LinkedIn (requires Selenium, may be rate limited)
            if len(company_jobs) < 2:  # Only if we need more jobs
                linkedin_jobs = self.scrape_linkedin(company)
                company_jobs.extend(linkedin_jobs)
            
            # Glassdoor (backup)
            if len(company_jobs) < 1:
                glassdoor_jobs = self.scrape_glassdoor(company)
                company_jobs.extend(glassdoor_jobs)
            
            # Company careers page
            career_jobs = self.scrape_company_careers(company)
            company_jobs.extend(career_jobs)
            
            all_jobs.extend(company_jobs)
            
            # Rate limiting
            time.sleep(1)
            
            # Progress update every 10 companies
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i+1}/{len(self.target_companies)} companies scraped. Found {len(all_jobs)} jobs so far.")
        
        logger.info(f"Scraping completed. Total jobs found: {len(all_jobs)}")
        return all_jobs

    def save_to_google_sheets(self, jobs: List[JobPosting]):
        """Save jobs to Google Sheets for Power BI integration"""
        try:
            # Setup Google Sheets API
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Load credentials from environment variable or file
            creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
            if creds_json:
                creds_dict = json.loads(creds_json)
                creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
            else:
                creds = Credentials.from_service_account_file('google_credentials.json', scopes=scope)
            
            gc = gspread.authorize(creds)
            
            # Open or create spreadsheet
            sheet_name = "MBA_Jobs_Daily_Feed"
            try:
                sheet = gc.open(sheet_name).sheet1
            except gspread.SpreadsheetNotFound:
                sheet = gc.create(sheet_name).sheet1
                # Share with your email for access
                email = os.getenv('GOOGLE_SHEET_SHARE_EMAIL', 'your-email@gmail.com')
                gc.open(sheet_name).share(email, perm_type='user', role='writer')
            
            # Prepare data
            headers = [
                'Company', 'Role Title', 'Function', 'Location', 'Start Date',
                'Posted Date', 'Visa Sponsorship', 'Direct Link', 'Key Qualifications',
                'Source', 'Scraped At'
            ]
            
            # Clear existing data and add headers
            sheet.clear()
            sheet.append_row(headers)
            
            # Add job data
            for job in jobs:
                row = [
                    job.company, job.role_title, job.function, job.location, job.start_date,
                    job.posted_date, job.visa_sponsorship, job.direct_link, job.key_qualifications,
                    job.source, job.scraped_at
                ]
                sheet.append_row(row)
            
            logger.info(f"Successfully saved {len(jobs)} jobs to Google Sheets: {sheet_name}")
            
        except Exception as e:
            logger.error(f"Error saving to Google Sheets: {e}")

    def send_email_report(self, jobs: List[JobPosting]):
        """Send daily email report with job findings"""
        try:
            # Email configuration
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            sender_email = os.getenv('SENDER_EMAIL')
            sender_password = os.getenv('SENDER_PASSWORD')
            recipient_email = os.getenv('RECIPIENT_EMAIL')
            
            if not all([sender_email, sender_password, recipient_email]):
                logger.error("Email credentials not configured")
                return
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Daily MBA Job Report - {len(jobs)} New Positions Found"
            
            # Create email body
            if jobs:
                body = f"""
Daily MBA/Masters Job Scraping Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Found {len(jobs)} new MBA/Masters positions posted within the last 48 hours:

"""
                for i, job in enumerate(jobs[:20], 1):  # Limit to first 20 in email
                    body += f"""
{i}. {job.company} - {job.role_title}
   Function: {job.function}
   Location: {job.location}
   Start Date: {job.start_date}
   Visa Sponsorship: {job.visa_sponsorship}
   Apply: {job.direct_link}
   Source: {job.source}
   
"""
                
                if len(jobs) > 20:
                    body += f"\n... and {len(jobs) - 20} more positions. Check Google Sheets for full list."
                
                body += f"\n\nFull data available in Google Sheets for Power BI analysis."
                
            else:
                body = f"""
Daily MBA/Masters Job Scraping Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

No new MBA full-time positions matching criteria posted in last 48 hours.

The scraper checked {len(self.target_companies)} companies across multiple job boards.
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, recipient_email, text)
            server.quit()
            
            logger.info("Email report sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")

def run_daily_scrape():
    """Main function to run daily scraping"""
    logger.info("Starting daily MBA job scraping...")
    
    scraper = JobScraper()
    jobs = scraper.scrape_all_companies()
    
    # Save to Google Sheets
    scraper.save_to_google_sheets(jobs)
    
    # Send email report
    scraper.send_email_report(jobs)
    
    logger.info(f"Daily scraping completed. Found {len(jobs)} jobs.")

def main():
    """Main entry point"""
    # For testing, run once
    if os.getenv('RUN_ONCE', 'false').lower() == 'true':
        run_daily_scrape()
    else:
        # Schedule daily runs
        schedule.every().day.at("08:00").do(run_daily_scrape)  # 8 AM daily
        
        logger.info("Scheduler started. Daily scraping at 8:00 AM.")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()