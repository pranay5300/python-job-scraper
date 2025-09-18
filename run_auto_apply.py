#!/usr/bin/env python3
"""
Quick start script for LinkedIn Auto-Apply
Simplified interface for common operations
"""

import os
import sys
import logging
from pathlib import Path
import argparse

def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def check_requirements():
    """Check if all required files and dependencies exist"""
    logger = logging.getLogger(__name__)
    
    required_files = [
        'main_auto_apply.py',
        'linkedin_auto_apply.py',
        'config_auto_apply.py',
        'safety_manager.py',
        'resume_manager.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Missing required files: {', '.join(missing_files)}")
        return False
    
    # Check for configuration
    if not Path('.env').exists() and not Path('auto_apply_config.json').exists():
        logger.warning("No configuration files found. Please set up .env or auto_apply_config.json")
        return False
    
    logger.info("✅ All required files found")
    return True

def quick_setup():
    """Quick setup wizard"""
    logger = logging.getLogger(__name__)
    
    print("🚀 LinkedIn Auto-Apply Quick Setup")
    print("=" * 50)
    
    # Check if .env exists
    if not Path('.env').exists():
        print("\n📝 Creating .env file...")
        
        # Get basic credentials
        linkedin_email = input("LinkedIn Email: ")
        linkedin_password = input("LinkedIn Password: ")
        linkedin_phone = input("LinkedIn Phone (optional): ")
        
        email_for_reports = input("Email for reports: ")
        email_password = input("Email password (Gmail App Password): ")
        
        # Create .env file
        env_content = f"""# LinkedIn Credentials
LINKEDIN_EMAIL={linkedin_email}
LINKEDIN_PASSWORD={linkedin_password}
LINKEDIN_PHONE={linkedin_phone}

# Email Configuration
SENDER_EMAIL={email_for_reports}
SENDER_PASSWORD={email_password}
RECIPIENT_EMAIL={email_for_reports}

# Safety Settings (recommended defaults)
MAX_APPLICATIONS_PER_DAY=15
MAX_APPLICATIONS_PER_HOUR=3
MAX_APPLICATIONS_PER_COMPANY=2
MIN_DELAY_BETWEEN_APPLICATIONS=60
MAX_DELAY_BETWEEN_APPLICATIONS=180

# Browser Settings
HEADLESS=false
LOG_LEVEL=INFO
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        logger.info("✅ .env file created")
    
    # Check for resume
    resume_files = list(Path('.').glob('*.pdf'))
    if not resume_files and not Path('resumes').exists():
        print("\n📄 No resume found. Please:")
        print("1. Place your resume.pdf in this directory, OR")
        print("2. Create a 'resumes' folder with your resume versions")
        
        resume_path = input("Enter path to your resume (or press Enter to skip): ")
        if resume_path and Path(resume_path).exists():
            # Setup resume versions
            os.system(f"python main_auto_apply.py --setup-resumes '{resume_path}'")
    
    print("\n✅ Quick setup completed!")
    print("You can now run:")
    print("  python run_auto_apply.py --test     # Test the system")
    print("  python run_auto_apply.py --run      # Apply to jobs")

def run_test():
    """Run system test"""
    logger = logging.getLogger(__name__)
    logger.info("🧪 Testing LinkedIn Auto-Apply System...")
    
    exit_code = os.system("python main_auto_apply.py --mode test")
    
    if exit_code == 0:
        logger.info("🎉 System test passed! Ready to apply to jobs.")
        return True
    else:
        logger.error("❌ System test failed. Please check configuration.")
        return False

def run_single_session(max_applications=10):
    """Run a single application session"""
    logger = logging.getLogger(__name__)
    logger.info(f"🎯 Starting application session (max {max_applications} applications)...")
    
    exit_code = os.system(f"python main_auto_apply.py --mode single --max-applications {max_applications}")
    
    if exit_code == 0:
        logger.info("✅ Application session completed!")
    else:
        logger.error("❌ Application session failed.")

def run_scheduled():
    """Run scheduled sessions"""
    logger = logging.getLogger(__name__)
    logger.info("📅 Starting scheduled LinkedIn Auto-Apply sessions...")
    logger.info("Press Ctrl+C to stop")
    
    os.system("python main_auto_apply.py --mode scheduled")

def show_status():
    """Show system status and recent activity"""
    logger = logging.getLogger(__name__)
    
    print("📊 LinkedIn Auto-Apply Status")
    print("=" * 40)
    
    # Check if log file exists
    if Path('linkedin_auto_apply.log').exists():
        print("📄 Recent log entries:")
        os.system("tail -10 linkedin_auto_apply.log")
    else:
        print("No log file found")
    
    # Check if database exists
    if Path('safety_tracking.db').exists():
        print("\n📈 Safety tracking database found")
        # Could add more detailed stats here
    
    # Check configuration
    if Path('.env').exists():
        print("✅ Configuration file (.env) found")
    if Path('auto_apply_config.json').exists():
        print("✅ JSON configuration found")
    
    # Check resume directory
    if Path('resumes').exists():
        resume_count = len(list(Path('resumes').glob('*.pdf')))
        print(f"📄 {resume_count} resume versions found")

def main():
    """Main entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(description="LinkedIn Auto-Apply Quick Runner")
    parser.add_argument('--setup', action='store_true', help='Run quick setup wizard')
    parser.add_argument('--test', action='store_true', help='Test system components')
    parser.add_argument('--run', type=int, default=10, help='Run single session (default: 10 applications)')
    parser.add_argument('--scheduled', action='store_true', help='Run scheduled sessions')
    parser.add_argument('--status', action='store_true', help='Show system status')
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if len(sys.argv) == 1:
        print("🤖 LinkedIn Auto-Apply for Supply Chain Roles")
        print("=" * 50)
        print("Quick commands:")
        print("  --setup      First-time setup wizard")
        print("  --test       Test all system components")
        print("  --run N      Apply to N jobs (default: 10)")
        print("  --scheduled  Run automated daily sessions")
        print("  --status     Show system status")
        print("\nFor advanced options, use main_auto_apply.py directly")
        return
    
    try:
        if args.setup:
            quick_setup()
        
        elif args.test:
            if not check_requirements():
                sys.exit(1)
            if not run_test():
                sys.exit(1)
        
        elif args.run:
            if not check_requirements():
                sys.exit(1)
            run_single_session(args.run)
        
        elif args.scheduled:
            if not check_requirements():
                sys.exit(1)
            run_scheduled()
        
        elif args.status:
            show_status()
        
    except KeyboardInterrupt:
        logger.info("⚠️ Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()