#!/usr/bin/env python3
"""
Configuration Management for LinkedIn Auto-Apply System
Centralized configuration for all components
"""

import os
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class LinkedInConfig:
    """LinkedIn-specific configuration"""
    email: str = ""
    password: str = ""
    phone: str = ""
    profile_url: str = ""

@dataclass
class SimplifyConfig:
    """Simplify platform configuration"""
    api_key: str = ""
    user_token: str = ""
    email: str = ""
    password: str = ""
    enabled: bool = True

@dataclass
class SafetyConfig:
    """Safety and rate limiting configuration"""
    max_applications_per_day: int = 25
    max_applications_per_hour: int = 5
    max_applications_per_company: int = 2
    min_delay_between_applications: int = 45
    max_delay_between_applications: int = 120
    max_page_views_per_hour: int = 100
    max_search_queries_per_hour: int = 20
    cooldown_period_hours: int = 2
    enable_human_simulation: bool = True
    enable_stealth_mode: bool = True

@dataclass
class SearchConfig:
    """Job search configuration"""
    target_locations: List[str] = None
    experience_levels: List[str] = None
    job_types: List[str] = None
    date_posted: str = "past-week"  # past-24-hours, past-week, past-month
    salary_range: Dict[str, int] = None
    remote_work: bool = True
    
    def __post_init__(self):
        if self.target_locations is None:
            self.target_locations = ["United States", "Remote"]
        if self.experience_levels is None:
            self.experience_levels = ["Entry level", "Associate"]
        if self.job_types is None:
            self.job_types = ["Full-time"]
        if self.salary_range is None:
            self.salary_range = {"min": 60000, "max": 120000}

@dataclass
class ResumeConfig:
    """Resume management configuration"""
    resume_directory: str = "resumes"
    auto_select_best_resume: bool = True
    create_specialized_versions: bool = True
    backup_enabled: bool = True
    backup_frequency_days: int = 7

@dataclass
class EmailConfig:
    """Email notification configuration"""
    enabled: bool = True
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = ""
    sender_password: str = ""
    recipient_email: str = ""
    daily_report: bool = True
    error_notifications: bool = True

@dataclass
class GoogleSheetsConfig:
    """Google Sheets integration configuration"""
    enabled: bool = True
    credentials_json: str = ""
    spreadsheet_name: str = "LinkedIn_Auto_Apply_Tracker"
    share_email: str = ""
    auto_backup: bool = True

@dataclass
class BrowserConfig:
    """Browser automation configuration"""
    headless: bool = False
    window_size: tuple = (1366, 768)
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    chrome_binary_path: str = ""
    chromedriver_path: str = ""
    download_directory: str = "downloads"

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    file_enabled: bool = True
    file_path: str = "linkedin_auto_apply.log"
    console_enabled: bool = True
    max_file_size_mb: int = 10
    backup_count: int = 5

class AutoApplyConfig:
    """Main configuration class for LinkedIn Auto-Apply system"""
    
    def __init__(self, config_file: str = "auto_apply_config.json"):
        self.config_file = config_file
        
        # Initialize configuration sections
        self.linkedin = LinkedInConfig()
        self.simplify = SimplifyConfig()
        self.safety = SafetyConfig()
        self.search = SearchConfig()
        self.resume = ResumeConfig()
        self.email = EmailConfig()
        self.google_sheets = GoogleSheetsConfig()
        self.browser = BrowserConfig()
        self.logging = LoggingConfig()
        
        # Load configuration
        self.load_config()
        self.load_from_environment()
        
        # Validate configuration
        self.validate_config()

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Update configuration sections
                if 'linkedin' in config_data:
                    self._update_dataclass(self.linkedin, config_data['linkedin'])
                if 'simplify' in config_data:
                    self._update_dataclass(self.simplify, config_data['simplify'])
                if 'safety' in config_data:
                    self._update_dataclass(self.safety, config_data['safety'])
                if 'search' in config_data:
                    self._update_dataclass(self.search, config_data['search'])
                if 'resume' in config_data:
                    self._update_dataclass(self.resume, config_data['resume'])
                if 'email' in config_data:
                    self._update_dataclass(self.email, config_data['email'])
                if 'google_sheets' in config_data:
                    self._update_dataclass(self.google_sheets, config_data['google_sheets'])
                if 'browser' in config_data:
                    self._update_dataclass(self.browser, config_data['browser'])
                if 'logging' in config_data:
                    self._update_dataclass(self.logging, config_data['logging'])
                
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                logger.info(f"Configuration file {self.config_file} not found. Using defaults.")
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")

    def load_from_environment(self):
        """Load configuration from environment variables"""
        try:
            # LinkedIn credentials
            self.linkedin.email = os.getenv('LINKEDIN_EMAIL', self.linkedin.email)
            self.linkedin.password = os.getenv('LINKEDIN_PASSWORD', self.linkedin.password)
            self.linkedin.phone = os.getenv('LINKEDIN_PHONE', self.linkedin.phone)
            
            # Simplify credentials
            self.simplify.api_key = os.getenv('SIMPLIFY_API_KEY', self.simplify.api_key)
            self.simplify.user_token = os.getenv('SIMPLIFY_USER_TOKEN', self.simplify.user_token)
            self.simplify.email = os.getenv('SIMPLIFY_EMAIL', self.simplify.email)
            self.simplify.password = os.getenv('SIMPLIFY_PASSWORD', self.simplify.password)
            
            # Email configuration
            self.email.sender_email = os.getenv('SENDER_EMAIL', self.email.sender_email)
            self.email.sender_password = os.getenv('SENDER_PASSWORD', self.email.sender_password)
            self.email.recipient_email = os.getenv('RECIPIENT_EMAIL', self.email.recipient_email)
            
            # Google Sheets
            self.google_sheets.credentials_json = os.getenv('GOOGLE_CREDENTIALS_JSON', self.google_sheets.credentials_json)
            self.google_sheets.share_email = os.getenv('GOOGLE_SHEET_SHARE_EMAIL', self.google_sheets.share_email)
            
            # Safety limits
            self.safety.max_applications_per_day = int(os.getenv('MAX_APPLICATIONS_PER_DAY', str(self.safety.max_applications_per_day)))
            self.safety.max_applications_per_company = int(os.getenv('MAX_APPLICATIONS_PER_COMPANY', str(self.safety.max_applications_per_company)))
            
            # Browser settings
            self.browser.headless = os.getenv('HEADLESS', 'false').lower() == 'true'
            self.browser.chrome_binary_path = os.getenv('CHROME_BIN', self.browser.chrome_binary_path)
            self.browser.chromedriver_path = os.getenv('CHROMEDRIVER_PATH', self.browser.chromedriver_path)
            
            logger.info("Environment variables loaded")
            
        except Exception as e:
            logger.error(f"Error loading environment variables: {e}")

    def _update_dataclass(self, dataclass_obj, data_dict):
        """Update dataclass object with dictionary data"""
        for key, value in data_dict.items():
            if hasattr(dataclass_obj, key):
                setattr(dataclass_obj, key, value)

    def validate_config(self):
        """Validate configuration settings"""
        errors = []
        warnings = []
        
        # Validate LinkedIn credentials
        if not self.linkedin.email or not self.linkedin.password:
            errors.append("LinkedIn email and password are required")
        
        # Validate email configuration if enabled
        if self.email.enabled:
            if not self.email.sender_email or not self.email.sender_password:
                warnings.append("Email notifications enabled but credentials not provided")
            if not self.email.recipient_email:
                warnings.append("Email notifications enabled but recipient not specified")
        
        # Validate Google Sheets configuration if enabled
        if self.google_sheets.enabled:
            if not self.google_sheets.credentials_json:
                warnings.append("Google Sheets enabled but credentials not provided")
        
        # Validate safety limits
        if self.safety.max_applications_per_day <= 0:
            errors.append("Max applications per day must be greater than 0")
        if self.safety.min_delay_between_applications >= self.safety.max_delay_between_applications:
            errors.append("Min delay must be less than max delay")
        
        # Validate search configuration
        if not self.search.target_locations:
            warnings.append("No target locations specified")
        
        # Log validation results
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            raise ValueError("Configuration validation failed")
        
        if warnings:
            for warning in warnings:
                logger.warning(f"Configuration warning: {warning}")
        
        logger.info("Configuration validation completed")

    def save_config(self):
        """Save current configuration to file"""
        try:
            config_data = {
                'linkedin': asdict(self.linkedin),
                'simplify': asdict(self.simplify),
                'safety': asdict(self.safety),
                'search': asdict(self.search),
                'resume': asdict(self.resume),
                'email': asdict(self.email),
                'google_sheets': asdict(self.google_sheets),
                'browser': asdict(self.browser),
                'logging': asdict(self.logging)
            }
            
            # Remove sensitive data before saving
            config_data['linkedin']['password'] = '***'
            config_data['simplify']['password'] = '***'
            config_data['email']['sender_password'] = '***'
            config_data['google_sheets']['credentials_json'] = '***'
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def get_supply_chain_keywords(self) -> List[str]:
        """Get supply chain specific keywords for job searching"""
        return [
            # Core supply chain terms
            "supply chain", "logistics", "operations", "procurement", "sourcing",
            "inventory management", "distribution", "manufacturing", "planning",
            "demand planning", "supply planning", "vendor management",
            
            # Program types
            "rotational program", "leadership development", "graduate program",
            "management trainee", "development program", "early career",
            
            # Skills and tools
            "lean manufacturing", "six sigma", "process improvement",
            "ERP systems", "SAP", "Oracle", "data analysis", "Excel",
            "project management", "continuous improvement",
            
            # Industry specific
            "warehouse management", "transportation", "freight",
            "supplier relations", "cost reduction", "quality control",
            "inventory optimization", "forecasting", "S&OP"
        ]

    def get_target_companies(self) -> List[str]:
        """Get list of target companies for supply chain roles"""
        return [
            # Technology
            "Amazon", "Microsoft", "Google", "Apple", "Meta", "Tesla", "Intel",
            "Cisco", "Dell Technologies", "HP Inc", "IBM", "Oracle", "Salesforce",
            
            # Retail & E-commerce
            "Walmart", "Target", "Home Depot", "Costco", "Best Buy", "Lowe's",
            "Kroger", "CVS Health", "Walgreens", "Dollar General",
            
            # Manufacturing
            "General Electric", "3M", "Boeing", "Lockheed Martin", "Caterpillar",
            "John Deere", "Ford", "General Motors", "Honeywell", "Emerson",
            
            # Consumer Goods
            "Procter & Gamble", "Unilever", "Johnson & Johnson", "PepsiCo",
            "Coca-Cola", "Nestle", "Mars", "Mondelez", "Kellogg", "General Mills",
            
            # Logistics & Transportation
            "FedEx", "UPS", "DHL", "C.H. Robinson", "XPO Logistics", "Ryder",
            "J.B. Hunt", "Schneider", "Old Dominion", "Expeditors",
            
            # Healthcare & Pharma
            "Pfizer", "Merck", "AbbVie", "Bristol Myers Squibb", "Eli Lilly",
            "Amgen", "Gilead", "Moderna", "Cardinal Health", "McKesson",
            
            # Energy & Chemicals
            "ExxonMobil", "Chevron", "ConocoPhillips", "Dow", "DuPont",
            "LyondellBasell", "Eastman Chemical", "PPG Industries",
            
            # Aerospace & Defense
            "Raytheon", "Northrop Grumman", "L3Harris", "General Dynamics",
            "BAE Systems", "Textron", "Spirit AeroSystems",
            
            # Food & Agriculture
            "Tyson Foods", "Cargill", "ADM", "Bunge", "JBS", "Hormel",
            "ConAgra", "Campbell Soup", "Kraft Heinz"
        ]

    def get_job_search_queries(self) -> List[str]:
        """Get optimized job search queries for supply chain roles"""
        return [
            "supply chain rotational program",
            "supply chain leadership development program",
            "operations rotational program",
            "logistics management trainee",
            "supply chain analyst entry level",
            "operations management graduate program",
            "procurement analyst entry level",
            "supply chain coordinator",
            "inventory analyst",
            "demand planning analyst",
            "supply planning analyst",
            "operations analyst entry level",
            "logistics coordinator",
            "vendor management specialist",
            "supply chain associate",
            "operations associate",
            "manufacturing analyst",
            "distribution analyst",
            "warehouse operations analyst",
            "transportation analyst"
        ]

    def create_default_config_file(self):
        """Create a default configuration file"""
        try:
            default_config = {
                "linkedin": {
                    "email": "your-linkedin-email@example.com",
                    "password": "your-linkedin-password",
                    "phone": "your-phone-number"
                },
                "simplify": {
                    "enabled": True,
                    "email": "your-simplify-email@example.com",
                    "password": "your-simplify-password"
                },
                "safety": {
                    "max_applications_per_day": 25,
                    "max_applications_per_hour": 5,
                    "max_applications_per_company": 2,
                    "min_delay_between_applications": 45,
                    "max_delay_between_applications": 120,
                    "enable_human_simulation": True,
                    "enable_stealth_mode": True
                },
                "search": {
                    "target_locations": ["United States", "Remote"],
                    "experience_levels": ["Entry level", "Associate"],
                    "job_types": ["Full-time"],
                    "date_posted": "past-week",
                    "remote_work": True
                },
                "resume": {
                    "resume_directory": "resumes",
                    "auto_select_best_resume": True,
                    "create_specialized_versions": True
                },
                "email": {
                    "enabled": True,
                    "sender_email": "your-email@gmail.com",
                    "sender_password": "your-app-password",
                    "recipient_email": "recipient@gmail.com",
                    "daily_report": True
                },
                "google_sheets": {
                    "enabled": True,
                    "spreadsheet_name": "LinkedIn_Auto_Apply_Tracker",
                    "share_email": "your-email@gmail.com"
                },
                "browser": {
                    "headless": False,
                    "window_size": [1366, 768]
                },
                "logging": {
                    "level": "INFO",
                    "file_enabled": True,
                    "console_enabled": True
                }
            }
            
            with open("auto_apply_config_template.json", 'w') as f:
                json.dump(default_config, f, indent=2)
            
            logger.info("Default configuration template created: auto_apply_config_template.json")
            
        except Exception as e:
            logger.error(f"Error creating default config: {e}")

# Global configuration instance
config = AutoApplyConfig()

def get_config() -> AutoApplyConfig:
    """Get the global configuration instance"""
    return config

def reload_config():
    """Reload configuration from file and environment"""
    global config
    config = AutoApplyConfig()
    logger.info("Configuration reloaded")

if __name__ == "__main__":
    # Create default configuration template
    config.create_default_config_file()
    print("Default configuration template created!")
    print("Edit auto_apply_config_template.json and rename to auto_apply_config.json")
    print("Also set environment variables as needed.")