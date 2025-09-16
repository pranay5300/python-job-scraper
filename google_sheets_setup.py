"""
Google Sheets Setup Helper
Run this script to set up your Google Sheets integration
"""
import json
import gspread
from google.oauth2.service_account import Credentials
import os

def setup_google_sheets():
    """Setup Google Sheets for the first time"""
    print("Google Sheets Setup for MBA Job Scraper")
    print("=" * 50)
    
    # Check if credentials exist
    creds_file = 'google_credentials.json'
    if not os.path.exists(creds_file):
        print(f"\n❌ Google credentials file '{creds_file}' not found!")
        print("\nTo set up Google Sheets integration:")
        print("1. Go to Google Cloud Console (console.cloud.google.com)")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Sheets API and Google Drive API")
        print("4. Create a Service Account")
        print("5. Download the JSON credentials file")
        print("6. Rename it to 'google_credentials.json' and place in this directory")
        print("7. Run this script again")
        return False
    
    try:
        # Load credentials
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(creds_file, scopes=scope)
        gc = gspread.authorize(creds)
        
        print("✅ Google credentials loaded successfully!")
        
        # Create or access spreadsheet
        sheet_name = "MBA_Jobs_Daily_Feed"
        try:
            spreadsheet = gc.open(sheet_name)
            print(f"✅ Found existing spreadsheet: {sheet_name}")
        except gspread.SpreadsheetNotFound:
            spreadsheet = gc.create(sheet_name)
            print(f"✅ Created new spreadsheet: {sheet_name}")
        
        # Share with your email
        email = input("\nEnter your email address to share the spreadsheet: ").strip()
        if email:
            spreadsheet.share(email, perm_type='user', role='writer')
            print(f"✅ Shared spreadsheet with {email}")
        
        # Setup headers
        worksheet = spreadsheet.sheet1
        headers = [
            'Company', 'Role Title', 'Function', 'Location', 'Start Date',
            'Posted Date', 'Visa Sponsorship', 'Direct Link', 'Key Qualifications',
            'Source', 'Scraped At'
        ]
        
        try:
            worksheet.append_row(headers)
            print("✅ Added headers to spreadsheet")
        except:
            print("ℹ️ Headers may already exist")
        
        print(f"\n🎉 Google Sheets setup complete!")
        print(f"📊 Spreadsheet URL: {spreadsheet.url}")
        print(f"📧 Shared with: {email}")
        
        # Save credentials as environment variable format
        with open(creds_file, 'r') as f:
            creds_dict = json.load(f)
        
        print(f"\n📝 For deployment, set this environment variable:")
        print(f"GOOGLE_CREDENTIALS_JSON='{json.dumps(creds_dict)}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Google Sheets: {e}")
        return False

if __name__ == "__main__":
    setup_google_sheets()