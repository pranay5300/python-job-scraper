#!/usr/bin/env python3
"""
LinkedIn Auto-Apply for Supply Chain Rotational Programs
Automatically applies to supply chain roles across USA using LinkedIn
"""

import time
import random
import logging
import json
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, 
    ElementClickInterceptedException, StaleElementReferenceException
)
import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_auto_apply.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class JobApplication:
    company: str
    job_title: str
    location: str
    job_url: str
    application_status: str
    applied_date: str
    job_description: str
    requirements_match: str
    salary_range: str
    application_method: str
    notes: str
    simplify_match: bool = False
    simplify_score: float = 0.0

@dataclass
class LinkedInCredentials:
    email: str
    password: str
    phone: str = ""
    
@dataclass
class ApplicationConfig:
    max_applications_per_day: int = 50
    max_applications_per_company: int = 3
    delay_between_applications: Tuple[int, int] = (30, 60)  # seconds
    required_keywords: List[str] = None
    excluded_keywords: List[str] = None
    target_locations: List[str] = None
    experience_levels: List[str] = None

class LinkedInAutoApply:
    def __init__(self, credentials: LinkedInCredentials, config: ApplicationConfig):
        self.credentials = credentials
        self.config = config
        self.driver = None
        self.applications_today = 0
        self.company_application_count = {}
        self.applied_jobs = set()
        self.failed_applications = []
        
        # Supply Chain specific settings
        self.supply_chain_keywords = [
            "supply chain", "logistics", "operations", "procurement", "sourcing",
            "inventory", "distribution", "manufacturing", "planning", "demand planning",
            "supply planning", "operations management", "lean", "six sigma",
            "rotational program", "leadership development", "graduate program"
        ]
        
        self.rotational_program_keywords = [
            "rotational", "rotation", "leadership development", "graduate program",
            "management trainee", "development program", "early career",
            "new graduate", "recent graduate", "entry level"
        ]
        
        # Companies with strong supply chain rotational programs
        self.target_companies = [
            "Amazon", "Walmart", "Target", "Home Depot", "Costco", "FedEx", "UPS",
            "DHL", "Procter & Gamble", "Unilever", "Johnson & Johnson", "3M",
            "General Electric", "Boeing", "Lockheed Martin", "Caterpillar",
            "John Deere", "Ford", "General Motors", "Tesla", "Apple", "Microsoft",
            "Google", "Meta", "Intel", "Cisco", "Dell Technologies", "HP Inc",
            "IBM", "Oracle", "Salesforce", "PepsiCo", "Coca-Cola", "Nestle",
            "Mars", "Mondelez", "Kraft Heinz", "General Mills", "Kellogg",
            "Tyson Foods", "Cargill", "ADM", "Bunge", "Louis Dreyfus",
            "Maersk", "CMA CGM", "COSCO", "MSC", "Hapag-Lloyd", "C.H. Robinson",
            "XPO Logistics", "Ryder", "Penske", "J.B. Hunt", "Schneider",
            "Knight-Swift", "Landstar", "Old Dominion", "YRC Worldwide",
            "Expeditors", "DSV", "Kuehne + Nagel", "DB Schenker", "CEVA Logistics"
        ]

    def setup_driver(self):
        """Setup Chrome driver with stealth settings"""
        chrome_options = Options()
        
        # Stealth settings to avoid detection
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Optional: Run headless for server deployment
        if os.getenv('HEADLESS', 'false').lower() == 'true':
            chrome_options.add_argument("--headless")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Chrome driver initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            return False

    def login_to_linkedin(self) -> bool:
        """Login to LinkedIn"""
        try:
            logger.info("Logging into LinkedIn...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for page load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            
            # Enter credentials
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            
            username_field.send_keys(self.credentials.email)
            time.sleep(random.uniform(1, 3))
            
            password_field.send_keys(self.credentials.password)
            time.sleep(random.uniform(1, 3))
            
            # Click login
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                logger.info("Successfully logged into LinkedIn")
                return True
            elif "challenge" in self.driver.current_url:
                logger.warning("LinkedIn security challenge detected. Manual intervention required.")
                input("Please complete the security challenge and press Enter to continue...")
                return True
            else:
                logger.error("Login failed")
                return False
                
        except Exception as e:
            logger.error(f"Error during LinkedIn login: {e}")
            return False

    def search_jobs(self, keywords: str, location: str = "United States", 
                   date_posted: str = "past-week") -> List[str]:
        """Search for jobs on LinkedIn"""
        job_urls = []
        
        try:
            # Construct search URL
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={keywords.replace(' ', '%20')}"
            search_url += f"&location={location.replace(' ', '%20')}"
            search_url += f"&f_TPR=r{self._get_date_filter(date_posted)}"
            search_url += "&f_E=2"  # Entry level
            search_url += "&f_JT=F"  # Full-time
            
            logger.info(f"Searching jobs with URL: {search_url}")
            self.driver.get(search_url)
            
            time.sleep(random.uniform(3, 5))
            
            # Scroll to load more jobs
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(2, 4))
            
            # Find job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-job-id]")
            
            for card in job_cards:
                try:
                    job_id = card.get_attribute("data-job-id")
                    if job_id:
                        job_url = f"https://www.linkedin.com/jobs/view/{job_id}"
                        if job_url not in self.applied_jobs:
                            job_urls.append(job_url)
                except:
                    continue
            
            logger.info(f"Found {len(job_urls)} job URLs")
            return job_urls[:50]  # Limit to 50 jobs per search
            
        except Exception as e:
            logger.error(f"Error searching jobs: {e}")
            return []

    def _get_date_filter(self, date_posted: str) -> str:
        """Convert date filter to LinkedIn format"""
        filters = {
            "past-24-hours": "86400",
            "past-week": "604800",
            "past-month": "2592000"
        }
        return filters.get(date_posted, "604800")

    def analyze_job(self, job_url: str) -> Tuple[bool, Dict]:
        """Analyze if job is suitable for application"""
        try:
            self.driver.get(job_url)
            time.sleep(random.uniform(3, 5))
            
            # Extract job details
            job_details = self._extract_job_details()
            
            if not job_details:
                return False, {}
            
            # Check if it's a supply chain role
            is_supply_chain = self._is_supply_chain_role(job_details)
            
            # Check if it's a rotational program
            is_rotational = self._is_rotational_program(job_details)
            
            # Check company
            is_target_company = any(company.lower() in job_details.get('company', '').lower() 
                                  for company in self.target_companies)
            
            # Check location (US-based)
            is_us_location = self._is_us_location(job_details.get('location', ''))
            
            # Check if already applied to this company recently
            company = job_details.get('company', '')
            if self.company_application_count.get(company, 0) >= self.config.max_applications_per_company:
                logger.info(f"Skipping {company} - already applied to {self.config.max_applications_per_company} positions")
                return False, job_details
            
            # Overall suitability score
            suitable = (is_supply_chain or is_rotational) and is_us_location
            
            if is_target_company:
                suitable = True  # Apply to target companies even if keywords don't match perfectly
            
            job_details['is_supply_chain'] = is_supply_chain
            job_details['is_rotational'] = is_rotational
            job_details['is_target_company'] = is_target_company
            job_details['suitable'] = suitable
            
            return suitable, job_details
            
        except Exception as e:
            logger.error(f"Error analyzing job {job_url}: {e}")
            return False, {}

    def _extract_job_details(self) -> Dict:
        """Extract job details from current page"""
        details = {}
        
        try:
            # Job title
            title_elem = self.driver.find_element(By.CSS_SELECTOR, "h1.top-card-layout__title")
            details['title'] = title_elem.text.strip()
            
            # Company
            company_elem = self.driver.find_element(By.CSS_SELECTOR, ".top-card-layout__card .top-card-layout__entity-info a")
            details['company'] = company_elem.text.strip()
            
            # Location
            location_elem = self.driver.find_element(By.CSS_SELECTOR, ".top-card-layout__card .top-card-layout__entity-info .top-card-layout__second-subline")
            details['location'] = location_elem.text.strip()
            
            # Job description
            try:
                show_more_btn = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Click to see more description']")
                show_more_btn.click()
                time.sleep(1)
            except:
                pass
            
            desc_elem = self.driver.find_element(By.CSS_SELECTOR, ".show-more-less-html__markup")
            details['description'] = desc_elem.text.strip()
            
            # Salary (if available)
            try:
                salary_elem = self.driver.find_element(By.CSS_SELECTOR, ".salary-main-rail__salary-info")
                details['salary'] = salary_elem.text.strip()
            except:
                details['salary'] = "Not specified"
            
            return details
            
        except Exception as e:
            logger.error(f"Error extracting job details: {e}")
            return {}

    def _is_supply_chain_role(self, job_details: Dict) -> bool:
        """Check if job is related to supply chain"""
        text = f"{job_details.get('title', '')} {job_details.get('description', '')}".lower()
        
        return any(keyword in text for keyword in self.supply_chain_keywords)

    def _is_rotational_program(self, job_details: Dict) -> bool:
        """Check if job is a rotational program"""
        text = f"{job_details.get('title', '')} {job_details.get('description', '')}".lower()
        
        return any(keyword in text for keyword in self.rotational_program_keywords)

    def _is_us_location(self, location: str) -> bool:
        """Check if location is in the US"""
        us_indicators = [
            "united states", "usa", "us", "america", "remote",
            "new york", "california", "texas", "florida", "illinois",
            "pennsylvania", "ohio", "georgia", "north carolina", "michigan",
            "new jersey", "virginia", "washington", "arizona", "massachusetts",
            "tennessee", "indiana", "missouri", "maryland", "wisconsin",
            "colorado", "minnesota", "south carolina", "alabama", "louisiana"
        ]
        
        location_lower = location.lower()
        return any(indicator in location_lower for indicator in us_indicators)

    def apply_to_job(self, job_url: str, job_details: Dict) -> JobApplication:
        """Apply to a specific job"""
        application = JobApplication(
            company=job_details.get('company', ''),
            job_title=job_details.get('title', ''),
            location=job_details.get('location', ''),
            job_url=job_url,
            application_status="Failed",
            applied_date=datetime.now().isoformat(),
            job_description=job_details.get('description', '')[:500] + "...",
            requirements_match="",
            salary_range=job_details.get('salary', ''),
            application_method="LinkedIn Easy Apply",
            notes=""
        )
        
        try:
            logger.info(f"Attempting to apply to: {job_details.get('company')} - {job_details.get('title')}")
            
            # Navigate to job page
            self.driver.get(job_url)
            time.sleep(random.uniform(3, 5))
            
            # Look for Easy Apply button
            easy_apply_btn = None
            try:
                easy_apply_btn = self.driver.find_element(By.CSS_SELECTOR, "[aria-label*='Easy Apply']")
            except:
                try:
                    easy_apply_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Easy Apply')]")
                except:
                    application.application_status = "No Easy Apply"
                    application.notes = "Easy Apply not available"
                    logger.warning("Easy Apply button not found")
                    return application
            
            # Click Easy Apply
            easy_apply_btn.click()
            time.sleep(random.uniform(2, 4))
            
            # Handle application flow
            success = self._handle_application_flow()
            
            if success:
                application.application_status = "Applied"
                self.applications_today += 1
                company = job_details.get('company', '')
                self.company_application_count[company] = self.company_application_count.get(company, 0) + 1
                self.applied_jobs.add(job_url)
                logger.info(f"Successfully applied to {company} - {job_details.get('title')}")
            else:
                application.application_status = "Failed"
                application.notes = "Application flow failed"
                
        except Exception as e:
            application.application_status = "Error"
            application.notes = str(e)
            logger.error(f"Error applying to job: {e}")
        
        return application

    def _handle_application_flow(self) -> bool:
        """Handle the Easy Apply application flow"""
        try:
            max_steps = 5
            current_step = 0
            
            while current_step < max_steps:
                time.sleep(random.uniform(2, 4))
                
                # Check if we're on the final submit page
                if self._is_final_submit_page():
                    return self._submit_final_application()
                
                # Fill current page
                self._fill_current_page()
                
                # Look for Next button
                next_btn = None
                try:
                    next_btn = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Continue') or contains(@aria-label, 'Next') or contains(text(), 'Next')]")
                except:
                    try:
                        next_btn = self.driver.find_element(By.CSS_SELECTOR, "[aria-label*='Next']")
                    except:
                        # Might be on final page
                        if self._is_final_submit_page():
                            return self._submit_final_application()
                        else:
                            logger.warning("Cannot find Next button and not on final page")
                            return False
                
                # Click Next
                if next_btn and next_btn.is_enabled():
                    next_btn.click()
                    current_step += 1
                else:
                    break
            
            # If we've gone through all steps, try to submit
            return self._submit_final_application()
            
        except Exception as e:
            logger.error(f"Error in application flow: {e}")
            return False

    def _fill_current_page(self):
        """Fill out the current application page"""
        try:
            # Fill phone number if requested
            phone_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='tel'], input[id*='phone'], input[name*='phone']")
            for phone_input in phone_inputs:
                if not phone_input.get_attribute('value') and self.credentials.phone:
                    phone_input.clear()
                    phone_input.send_keys(self.credentials.phone)
                    time.sleep(random.uniform(0.5, 1.5))
            
            # Handle dropdowns with common responses
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            for select_elem in selects:
                try:
                    select = Select(select_elem)
                    options = [option.text.lower() for option in select.options]
                    
                    # Common responses for supply chain applications
                    if any("experience" in opt for opt in options):
                        if any("0-1" in opt or "entry" in opt or "less than 1" in opt for opt in options):
                            for option in select.options:
                                if "0-1" in option.text.lower() or "entry" in option.text.lower() or "less than 1" in option.text.lower():
                                    select.select_by_visible_text(option.text)
                                    break
                    
                    elif any("education" in opt for opt in options):
                        if any("bachelor" in opt or "master" in opt for opt in options):
                            for option in select.options:
                                if "master" in option.text.lower() or "bachelor" in option.text.lower():
                                    select.select_by_visible_text(option.text)
                                    break
                    
                    elif any("visa" in opt or "authorization" in opt for opt in options):
                        if any("yes" in opt or "authorized" in opt for opt in options):
                            for option in select.options:
                                if "yes" in option.text.lower() or "authorized" in option.text.lower():
                                    select.select_by_visible_text(option.text)
                                    break
                
                except Exception as e:
                    logger.warning(f"Could not handle dropdown: {e}")
                    continue
            
            # Handle radio buttons
            radio_groups = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
            handled_groups = set()
            
            for radio in radio_groups:
                try:
                    name = radio.get_attribute('name')
                    if name in handled_groups:
                        continue
                    
                    # Get all radios in this group
                    group_radios = self.driver.find_elements(By.CSS_SELECTOR, f"input[name='{name}']")
                    
                    # Find labels for context
                    question_text = ""
                    try:
                        parent = radio.find_element(By.XPATH, "./ancestor::fieldset[1]")
                        question_text = parent.text.lower()
                    except:
                        try:
                            parent = radio.find_element(By.XPATH, "./ancestor::div[contains(@class, 'form-group')][1]")
                            question_text = parent.text.lower()
                        except:
                            pass
                    
                    # Select appropriate response
                    for group_radio in group_radios:
                        try:
                            label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{group_radio.get_attribute('id')}']")
                            label_text = label.text.lower()
                            
                            # Supply chain specific responses
                            if ("visa" in question_text or "authorization" in question_text) and "yes" in label_text:
                                group_radio.click()
                                handled_groups.add(name)
                                break
                            elif ("experience" in question_text) and ("0" in label_text or "entry" in label_text):
                                group_radio.click()
                                handled_groups.add(name)
                                break
                            elif ("willing" in question_text or "relocate" in question_text) and "yes" in label_text:
                                group_radio.click()
                                handled_groups.add(name)
                                break
                        except:
                            continue
                
                except Exception as e:
                    continue
            
            # Handle text areas for cover letters
            text_areas = self.driver.find_elements(By.TAG_NAME, "textarea")
            for textarea in text_areas:
                if not textarea.get_attribute('value'):
                    # Add a brief, professional message
                    cover_letter = self._generate_cover_letter()
                    textarea.clear()
                    textarea.send_keys(cover_letter)
                    time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            logger.warning(f"Error filling current page: {e}")

    def _generate_cover_letter(self) -> str:
        """Generate a brief cover letter for supply chain roles"""
        templates = [
            "I am excited to apply for this supply chain position. With my background in operations and logistics, I am eager to contribute to your team's success and grow within your organization.",
            
            "I am interested in this supply chain opportunity as it aligns perfectly with my career goals in operations management. I look forward to bringing my analytical skills and passion for process improvement to your team.",
            
            "This supply chain role represents an excellent opportunity to apply my knowledge of logistics and operations. I am particularly drawn to your company's commitment to innovation and excellence in supply chain management."
        ]
        
        return random.choice(templates)

    def _is_final_submit_page(self) -> bool:
        """Check if we're on the final submit page"""
        try:
            submit_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Submit') or contains(@aria-label, 'Submit')]")
            review_text = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Review') or contains(text(), 'review')]")
            
            return len(submit_buttons) > 0 or len(review_text) > 0
        except:
            return False

    def _submit_final_application(self) -> bool:
        """Submit the final application"""
        try:
            # Look for submit button
            submit_btn = None
            try:
                submit_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Submit') or contains(@aria-label, 'Submit')]")
            except:
                try:
                    submit_btn = self.driver.find_element(By.CSS_SELECTOR, "[aria-label*='Submit']")
                except:
                    logger.warning("Could not find submit button")
                    return False
            
            if submit_btn and submit_btn.is_enabled():
                submit_btn.click()
                time.sleep(random.uniform(3, 5))
                
                # Check for confirmation
                confirmation_indicators = [
                    "application submitted",
                    "thank you",
                    "we'll be in touch",
                    "application received"
                ]
                
                page_text = self.driver.page_source.lower()
                if any(indicator in page_text for indicator in confirmation_indicators):
                    return True
                else:
                    # Sometimes the page redirects, check URL
                    if "jobs/application-submitted" in self.driver.current_url:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error submitting application: {e}")
            return False

    def run_application_batch(self, max_applications: int = None) -> List[JobApplication]:
        """Run a batch of applications"""
        if max_applications is None:
            max_applications = self.config.max_applications_per_day
        
        applications = []
        
        # Search queries for supply chain roles
        search_queries = [
            "supply chain rotational program",
            "supply chain leadership development",
            "operations rotational program",
            "logistics management trainee",
            "supply chain analyst entry level",
            "operations management graduate",
            "supply chain coordinator",
            "procurement analyst entry level",
            "inventory analyst",
            "demand planning analyst"
        ]
        
        try:
            logger.info(f"Starting application batch - Target: {max_applications} applications")
            
            for query in search_queries:
                if self.applications_today >= max_applications:
                    break
                
                logger.info(f"Searching for: {query}")
                job_urls = self.search_jobs(query)
                
                for job_url in job_urls:
                    if self.applications_today >= max_applications:
                        break
                    
                    if job_url in self.applied_jobs:
                        continue
                    
                    # Analyze job suitability
                    is_suitable, job_details = self.analyze_job(job_url)
                    
                    if is_suitable:
                        # Apply to job
                        application = self.apply_to_job(job_url, job_details)
                        applications.append(application)
                        
                        # Random delay between applications
                        delay = random.uniform(*self.config.delay_between_applications)
                        logger.info(f"Waiting {delay:.1f} seconds before next application...")
                        time.sleep(delay)
                    else:
                        logger.info(f"Skipping job - not suitable: {job_details.get('title', 'Unknown')}")
                
                # Delay between search queries
                time.sleep(random.uniform(10, 20))
            
            logger.info(f"Application batch completed. Applied to {self.applications_today} jobs today.")
            
        except Exception as e:
            logger.error(f"Error in application batch: {e}")
        
        return applications

    def save_applications_to_sheets(self, applications: List[JobApplication]):
        """Save applications to Google Sheets"""
        try:
            # Setup Google Sheets API
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
            if creds_json:
                creds_dict = json.loads(creds_json)
                creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
            else:
                creds = Credentials.from_service_account_file('google_credentials.json', scopes=scope)
            
            gc = gspread.authorize(creds)
            
            # Open or create spreadsheet
            sheet_name = "LinkedIn_Auto_Apply_Tracker"
            try:
                sheet = gc.open(sheet_name).sheet1
            except gspread.SpreadsheetNotFound:
                sheet = gc.create(sheet_name).sheet1
                # Share with your email
                email = os.getenv('GOOGLE_SHEET_SHARE_EMAIL', 'your-email@gmail.com')
                gc.open(sheet_name).share(email, perm_type='user', role='writer')
            
            # Prepare headers if sheet is empty
            if not sheet.get_all_values():
                headers = [
                    'Company', 'Job Title', 'Location', 'Job URL', 'Application Status',
                    'Applied Date', 'Job Description', 'Requirements Match', 'Salary Range',
                    'Application Method', 'Notes', 'Simplify Match', 'Simplify Score'
                ]
                sheet.append_row(headers)
            
            # Add application data
            for app in applications:
                row = [
                    app.company, app.job_title, app.location, app.job_url, app.application_status,
                    app.applied_date, app.job_description, app.requirements_match, app.salary_range,
                    app.application_method, app.notes, app.simplify_match, app.simplify_score
                ]
                sheet.append_row(row)
            
            logger.info(f"Successfully saved {len(applications)} applications to Google Sheets")
            
        except Exception as e:
            logger.error(f"Error saving to Google Sheets: {e}")

    def send_daily_report(self, applications: List[JobApplication]):
        """Send daily application report via email"""
        try:
            # Email configuration
            sender_email = os.getenv('SENDER_EMAIL')
            sender_password = os.getenv('SENDER_PASSWORD')
            recipient_email = os.getenv('RECIPIENT_EMAIL')
            
            if not all([sender_email, sender_password, recipient_email]):
                logger.warning("Email credentials not configured")
                return
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"LinkedIn Auto-Apply Report - {len(applications)} Applications Submitted"
            
            # Create email body
            successful_apps = [app for app in applications if app.application_status == "Applied"]
            failed_apps = [app for app in applications if app.application_status != "Applied"]
            
            body = f"""
Daily LinkedIn Auto-Apply Report
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Summary:
- Total Applications Attempted: {len(applications)}
- Successful Applications: {len(successful_apps)}
- Failed Applications: {len(failed_apps)}

Successful Applications:
"""
            
            for i, app in enumerate(successful_apps, 1):
                body += f"""
{i}. {app.company} - {app.job_title}
   Location: {app.location}
   Applied: {app.applied_date}
   Job URL: {app.job_url}
"""
            
            if failed_apps:
                body += f"\n\nFailed Applications ({len(failed_apps)}):\n"
                for i, app in enumerate(failed_apps, 1):
                    body += f"{i}. {app.company} - {app.job_title} (Reason: {app.application_status})\n"
            
            body += f"\n\nFull tracking data available in Google Sheets.\n"
            body += f"Total applications submitted today: {self.applications_today}"
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, recipient_email, text)
            server.quit()
            
            logger.info("Daily report sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending email report: {e}")

    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser driver closed")

def main():
    """Main execution function"""
    try:
        # Load configuration
        credentials = LinkedInCredentials(
            email=os.getenv('LINKEDIN_EMAIL'),
            password=os.getenv('LINKEDIN_PASSWORD'),
            phone=os.getenv('LINKEDIN_PHONE', '')
        )
        
        if not credentials.email or not credentials.password:
            logger.error("LinkedIn credentials not provided")
            return
        
        config = ApplicationConfig(
            max_applications_per_day=int(os.getenv('MAX_APPLICATIONS_PER_DAY', '25')),
            max_applications_per_company=int(os.getenv('MAX_APPLICATIONS_PER_COMPANY', '2')),
            delay_between_applications=(30, 60)
        )
        
        # Initialize auto-applier
        auto_apply = LinkedInAutoApply(credentials, config)
        
        # Setup driver and login
        if not auto_apply.setup_driver():
            logger.error("Failed to setup browser driver")
            return
        
        if not auto_apply.login_to_linkedin():
            logger.error("Failed to login to LinkedIn")
            return
        
        # Run application batch
        applications = auto_apply.run_application_batch()
        
        # Save results
        auto_apply.save_applications_to_sheets(applications)
        auto_apply.send_daily_report(applications)
        
        logger.info(f"Session completed. Total applications: {len(applications)}")
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        try:
            auto_apply.cleanup()
        except:
            pass

if __name__ == "__main__":
    main()