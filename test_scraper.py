"""
Test script for MBA Job Scraper
Run this to test the scraper with a small subset of companies
"""
import os
from mba_job_scraper import JobScraper
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_scraper():
    """Test the scraper with a few companies"""
    print("Testing MBA Job Scraper...")
    print("=" * 40)
    
    # Create scraper instance
    scraper = JobScraper()
    
    # Test with just a few companies
    test_companies = [
        "Amazon", "Microsoft", "Google", "Apple", "Meta",
        "JPMorgan", "Goldman Sachs", "McKinsey", "BCG", "Deloitte"
    ]
    
    # Override the target companies for testing
    scraper.target_companies = test_companies
    
    print(f"Testing with {len(test_companies)} companies:")
    for company in test_companies:
        print(f"  - {company}")
    
    # Run scraping
    jobs = scraper.scrape_all_companies()
    
    print(f"\n📊 Test Results:")
    print(f"Total jobs found: {len(jobs)}")
    
    if jobs:
        print(f"\n📋 Sample jobs:")
        for i, job in enumerate(jobs[:5], 1):
            print(f"{i}. {job.company} - {job.role_title}")
            print(f"   Function: {job.function}")
            print(f"   Location: {job.location}")
            print(f"   Source: {job.source}")
            print()
        
        # Test Google Sheets integration if credentials exist
        if os.path.exists('google_credentials.json') or os.getenv('GOOGLE_CREDENTIALS_JSON'):
            print("Testing Google Sheets integration...")
            try:
                scraper.save_to_google_sheets(jobs)
                print("✅ Google Sheets test successful!")
            except Exception as e:
                print(f"❌ Google Sheets test failed: {e}")
        else:
            print("ℹ️ Skipping Google Sheets test (no credentials)")
        
        # Test email if configured
        if all([os.getenv('SENDER_EMAIL'), os.getenv('SENDER_PASSWORD'), os.getenv('RECIPIENT_EMAIL')]):
            print("Testing email integration...")
            try:
                scraper.send_email_report(jobs)
                print("✅ Email test successful!")
            except Exception as e:
                print(f"❌ Email test failed: {e}")
        else:
            print("ℹ️ Skipping email test (not configured)")
    
    else:
        print("No jobs found. This could be normal if:")
        print("- No recent postings match criteria")
        print("- Rate limiting is blocking requests")
        print("- Websites have changed their structure")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    # Set environment variable to run once
    os.environ['RUN_ONCE'] = 'true'
    test_scraper()