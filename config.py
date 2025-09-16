"""
Configuration file for MBA Job Scraper
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Email Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD')  # Use App Password for Gmail
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

# Google Sheets Configuration
GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS_JSON')  # JSON string of service account
GOOGLE_SHEET_SHARE_EMAIL = os.getenv('GOOGLE_SHEET_SHARE_EMAIL')
SPREADSHEET_NAME = os.getenv('SPREADSHEET_NAME', 'MBA_Jobs_Daily_Feed')

# Scraping Configuration
RUN_ONCE = os.getenv('RUN_ONCE', 'false').lower() == 'true'
DAILY_RUN_TIME = os.getenv('DAILY_RUN_TIME', '08:00')
MAX_JOBS_PER_COMPANY = int(os.getenv('MAX_JOBS_PER_COMPANY', '5'))
REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '2.0'))

# Chrome Driver Configuration (for Render.com)
CHROME_BIN = os.getenv('CHROME_BIN', '/usr/bin/google-chrome')
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', '/usr/bin/chromedriver')