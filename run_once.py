#!/usr/bin/env python3
"""
Run the scraper once for testing or manual execution
"""
import os
import sys
from mba_job_scraper import run_daily_scrape

if __name__ == "__main__":
    # Set environment variable to run once
    os.environ['RUN_ONCE'] = 'true'
    
    print("🚀 Running MBA Job Scraper (one-time execution)")
    print("=" * 50)
    
    try:
        run_daily_scrape()
        print("\n✅ Scraping completed successfully!")
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        sys.exit(1)