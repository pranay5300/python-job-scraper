#!/usr/bin/env python3
"""
Main execution script for LinkedIn Auto-Apply System
Orchestrates all components for automated job applications
"""

import os
import sys
import time
import logging
import signal
import schedule
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import argparse
import json

# Import all modules
from linkedin_auto_apply import LinkedInAutoApply, LinkedInCredentials, ApplicationConfig
from simplify_integration import SimplifyAPI, integrate_simplify_with_linkedin
from resume_manager import ResumeManager, CoverLetterGenerator
from safety_manager import SafetyManager, SafetyLimits, LinkedInDetectionAvoidance
from config_auto_apply import AutoApplyConfig, get_config

# Configure logging
def setup_logging(config: AutoApplyConfig):
    """Setup logging configuration"""
    log_level = getattr(logging, config.logging.level.upper())
    
    handlers = []
    
    # Console handler
    if config.logging.console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        handlers.append(console_handler)
    
    # File handler
    if config.logging.file_enabled:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            config.logging.file_path,
            maxBytes=config.logging.max_file_size_mb * 1024 * 1024,
            backupCount=config.logging.backup_count
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger(__name__)

class LinkedInAutoApplyOrchestrator:
    """Main orchestrator for the LinkedIn Auto-Apply system"""
    
    def __init__(self, config: AutoApplyConfig):
        self.config = config
        self.running = False
        self.session_stats = {
            'start_time': None,
            'applications_submitted': 0,
            'applications_failed': 0,
            'companies_applied': set(),
            'errors': []
        }
        
        # Initialize components
        self.safety_manager = None
        self.resume_manager = None
        self.cover_letter_generator = None
        self.simplify_api = None
        self.linkedin_auto_apply = None
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def initialize_components(self):
        """Initialize all system components"""
        try:
            logger.info("Initializing LinkedIn Auto-Apply system components...")
            
            # Initialize Safety Manager
            safety_limits = SafetyLimits(
                max_applications_per_day=self.config.safety.max_applications_per_day,
                max_applications_per_hour=self.config.safety.max_applications_per_hour,
                max_applications_per_company=self.config.safety.max_applications_per_company,
                min_delay_between_applications=self.config.safety.min_delay_between_applications,
                max_delay_between_applications=self.config.safety.max_delay_between_applications,
                cooldown_period_hours=self.config.safety.cooldown_period_hours
            )
            self.safety_manager = SafetyManager(safety_limits)
            logger.info("✅ Safety Manager initialized")
            
            # Initialize Resume Manager
            self.resume_manager = ResumeManager(self.config.resume.resume_directory)
            self.cover_letter_generator = CoverLetterGenerator()
            logger.info("✅ Resume Manager initialized")
            
            # Initialize Simplify API (if enabled)
            if self.config.simplify.enabled:
                self.simplify_api = SimplifyAPI(
                    api_key=self.config.simplify.api_key,
                    user_token=self.config.simplify.user_token
                )
                
                # Authenticate if credentials provided
                if self.config.simplify.email and self.config.simplify.password:
                    if self.simplify_api.authenticate(self.config.simplify.email, self.config.simplify.password):
                        logger.info("✅ Simplify API authenticated")
                    else:
                        logger.warning("⚠️ Simplify authentication failed")
                        self.simplify_api = None
                else:
                    logger.info("✅ Simplify API initialized (no auth)")
            
            # Initialize LinkedIn Auto-Apply
            linkedin_creds = LinkedInCredentials(
                email=self.config.linkedin.email,
                password=self.config.linkedin.password,
                phone=self.config.linkedin.phone
            )
            
            app_config = ApplicationConfig(
                max_applications_per_day=self.config.safety.max_applications_per_day,
                max_applications_per_company=self.config.safety.max_applications_per_company,
                delay_between_applications=(
                    self.config.safety.min_delay_between_applications,
                    self.config.safety.max_delay_between_applications
                ),
                target_locations=self.config.search.target_locations,
                experience_levels=self.config.search.experience_levels
            )
            
            self.linkedin_auto_apply = LinkedInAutoApply(linkedin_creds, app_config)
            logger.info("✅ LinkedIn Auto-Apply initialized")
            
            logger.info("🚀 All components initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing components: {e}")
            return False

    def run_single_session(self, max_applications: int = None) -> Dict:
        """Run a single application session"""
        if max_applications is None:
            max_applications = self.config.safety.max_applications_per_day
        
        self.session_stats['start_time'] = datetime.now()
        session_results = {
            'applications': [],
            'success_count': 0,
            'failure_count': 0,
            'companies_applied': set(),
            'duration_minutes': 0,
            'errors': []
        }
        
        try:
            logger.info(f"🎯 Starting application session - Target: {max_applications} applications")
            
            # Check if we can start applying
            can_apply, reason = self.safety_manager.can_apply_to_job("")
            if not can_apply:
                logger.warning(f"⚠️ Cannot start session: {reason}")
                return session_results
            
            # Setup browser and login
            if not self.linkedin_auto_apply.setup_driver():
                raise Exception("Failed to setup browser driver")
            
            # Setup stealth mode
            if self.config.safety.enable_stealth_mode:
                stealth = LinkedInDetectionAvoidance(self.linkedin_auto_apply.driver)
                stealth.setup_stealth_mode()
                stealth.randomize_viewport_size()
            
            # Login to LinkedIn
            if not self.linkedin_auto_apply.login_to_linkedin():
                raise Exception("Failed to login to LinkedIn")
            
            self.safety_manager.record_activity("login", success=True)
            
            # Get Simplify recommendations if available
            simplify_applications = []
            if self.simplify_api:
                try:
                    simplify_applications = integrate_simplify_with_linkedin(
                        self.linkedin_auto_apply, self.simplify_api
                    )
                    logger.info(f"📊 Got {len(simplify_applications)} Simplify recommendations")
                except Exception as e:
                    logger.warning(f"⚠️ Simplify integration error: {e}")
            
            # Run main application batch
            applications = self.linkedin_auto_apply.run_application_batch(max_applications)
            
            # Combine with Simplify applications
            all_applications = applications + simplify_applications
            
            # Process results
            for app in all_applications:
                session_results['applications'].append(app)
                
                if app.application_status == "Applied":
                    session_results['success_count'] += 1
                    session_results['companies_applied'].add(app.company)
                    self.safety_manager.record_activity(
                        "application", company=app.company, job_title=app.job_title, success=True
                    )
                else:
                    session_results['failure_count'] += 1
                    self.safety_manager.record_activity(
                        "application", company=app.company, job_title=app.job_title, 
                        success=False, notes=app.notes
                    )
            
            # Save to Google Sheets
            if self.config.google_sheets.enabled and all_applications:
                try:
                    self.linkedin_auto_apply.save_applications_to_sheets(all_applications)
                    logger.info("📊 Results saved to Google Sheets")
                except Exception as e:
                    logger.error(f"❌ Error saving to Google Sheets: {e}")
                    session_results['errors'].append(f"Google Sheets error: {e}")
            
            # Send email report
            if self.config.email.enabled and all_applications:
                try:
                    self.linkedin_auto_apply.send_daily_report(all_applications)
                    logger.info("📧 Email report sent")
                except Exception as e:
                    logger.error(f"❌ Error sending email: {e}")
                    session_results['errors'].append(f"Email error: {e}")
            
            # Calculate session duration
            session_duration = datetime.now() - self.session_stats['start_time']
            session_results['duration_minutes'] = session_duration.total_seconds() / 60
            
            # Log session summary
            logger.info(f"✅ Session completed!")
            logger.info(f"   📊 Applications: {session_results['success_count']} successful, {session_results['failure_count']} failed")
            logger.info(f"   🏢 Companies: {len(session_results['companies_applied'])}")
            logger.info(f"   ⏱️ Duration: {session_results['duration_minutes']:.1f} minutes")
            
        except Exception as e:
            logger.error(f"❌ Session error: {e}")
            session_results['errors'].append(str(e))
        
        finally:
            # Cleanup
            try:
                self.linkedin_auto_apply.cleanup()
            except:
                pass
        
        return session_results

    def run_scheduled_sessions(self):
        """Run scheduled application sessions"""
        logger.info("📅 Starting scheduled LinkedIn Auto-Apply sessions")
        
        # Schedule daily sessions
        schedule.every().day.at("09:00").do(self._scheduled_session_wrapper)
        schedule.every().day.at("14:00").do(self._scheduled_session_wrapper)
        schedule.every().day.at("19:00").do(self._scheduled_session_wrapper)
        
        # Schedule weekly maintenance
        schedule.every().sunday.at("02:00").do(self._weekly_maintenance)
        
        self.running = True
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("⚠️ Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
        
        logger.info("📅 Scheduled sessions stopped")

    def _scheduled_session_wrapper(self):
        """Wrapper for scheduled sessions"""
        try:
            # Check if it's a good time to run (avoid weekends, late nights)
            now = datetime.now()
            
            # Skip weekends
            if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
                logger.info("⏭️ Skipping session - Weekend")
                return
            
            # Skip late night / early morning
            if now.hour < 8 or now.hour > 20:
                logger.info("⏭️ Skipping session - Outside business hours")
                return
            
            # Run session with reduced applications for scheduled runs
            max_apps = min(10, self.config.safety.max_applications_per_day // 3)
            results = self.run_single_session(max_apps)
            
            # Log scheduled session results
            logger.info(f"📅 Scheduled session completed: {results['success_count']} applications")
            
        except Exception as e:
            logger.error(f"❌ Scheduled session error: {e}")

    def _weekly_maintenance(self):
        """Perform weekly maintenance tasks"""
        try:
            logger.info("🔧 Running weekly maintenance...")
            
            # Cleanup old safety data
            self.safety_manager.cleanup_old_data(days_to_keep=30)
            
            # Backup resumes
            if self.config.resume.backup_enabled:
                self.resume_manager.backup_resumes()
            
            # Generate weekly report
            self._generate_weekly_report()
            
            logger.info("✅ Weekly maintenance completed")
            
        except Exception as e:
            logger.error(f"❌ Weekly maintenance error: {e}")

    def _generate_weekly_report(self):
        """Generate and send weekly performance report"""
        try:
            # Get safety report
            safety_report = self.safety_manager.get_safety_report()
            
            # Get resume usage stats
            resume_stats = self.resume_manager.get_resume_usage_stats()
            
            # Create comprehensive report
            report = {
                'week_ending': datetime.now().strftime('%Y-%m-%d'),
                'safety_metrics': safety_report,
                'resume_performance': resume_stats,
                'system_health': {
                    'components_active': True,
                    'last_successful_session': datetime.now().isoformat(),
                    'total_errors_this_week': len(self.session_stats.get('errors', []))
                }
            }
            
            # Save report to file
            report_file = f"weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"📊 Weekly report generated: {report_file}")
            
        except Exception as e:
            logger.error(f"❌ Error generating weekly report: {e}")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"⚠️ Received signal {signum}. Shutting down gracefully...")
        self.running = False
        
        try:
            if self.linkedin_auto_apply:
                self.linkedin_auto_apply.cleanup()
        except:
            pass

    def setup_resume_versions(self, base_resume_path: str) -> bool:
        """Setup specialized resume versions for supply chain roles"""
        try:
            if not os.path.exists(base_resume_path):
                logger.error(f"❌ Base resume not found: {base_resume_path}")
                return False
            
            success = self.resume_manager.create_supply_chain_resume_versions(base_resume_path)
            
            if success:
                logger.info("✅ Supply chain resume versions created")
                return True
            else:
                logger.error("❌ Failed to create resume versions")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error setting up resume versions: {e}")
            return False

    def test_system_components(self) -> Dict:
        """Test all system components"""
        test_results = {
            'safety_manager': False,
            'resume_manager': False,
            'linkedin_connection': False,
            'simplify_connection': False,
            'google_sheets': False,
            'email': False,
            'overall_status': False
        }
        
        try:
            logger.info("🧪 Testing system components...")
            
            # Test Safety Manager
            try:
                can_apply, reason = self.safety_manager.can_apply_to_job("Test Company")
                test_results['safety_manager'] = True
                logger.info("✅ Safety Manager: OK")
            except Exception as e:
                logger.error(f"❌ Safety Manager: {e}")
            
            # Test Resume Manager
            try:
                stats = self.resume_manager.get_resume_usage_stats()
                test_results['resume_manager'] = True
                logger.info("✅ Resume Manager: OK")
            except Exception as e:
                logger.error(f"❌ Resume Manager: {e}")
            
            # Test LinkedIn connection (without full login)
            try:
                if self.linkedin_auto_apply.setup_driver():
                    test_results['linkedin_connection'] = True
                    logger.info("✅ LinkedIn Connection: OK")
                    self.linkedin_auto_apply.cleanup()
            except Exception as e:
                logger.error(f"❌ LinkedIn Connection: {e}")
            
            # Test Simplify connection
            if self.simplify_api:
                try:
                    profile = self.simplify_api.get_user_profile()
                    test_results['simplify_connection'] = True
                    logger.info("✅ Simplify Connection: OK")
                except Exception as e:
                    logger.error(f"❌ Simplify Connection: {e}")
            
            # Test Google Sheets
            if self.config.google_sheets.enabled:
                try:
                    # Test with empty data
                    self.linkedin_auto_apply.save_applications_to_sheets([])
                    test_results['google_sheets'] = True
                    logger.info("✅ Google Sheets: OK")
                except Exception as e:
                    logger.error(f"❌ Google Sheets: {e}")
            
            # Test Email
            if self.config.email.enabled:
                try:
                    # Test with empty report
                    self.linkedin_auto_apply.send_daily_report([])
                    test_results['email'] = True
                    logger.info("✅ Email: OK")
                except Exception as e:
                    logger.error(f"❌ Email: {e}")
            
            # Overall status
            critical_components = ['safety_manager', 'resume_manager', 'linkedin_connection']
            test_results['overall_status'] = all(test_results[comp] for comp in critical_components)
            
            if test_results['overall_status']:
                logger.info("🎉 All critical components working!")
            else:
                logger.warning("⚠️ Some components have issues")
            
        except Exception as e:
            logger.error(f"❌ System test error: {e}")
        
        return test_results

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="LinkedIn Auto-Apply for Supply Chain Roles")
    parser.add_argument('--mode', choices=['single', 'scheduled', 'test'], default='single',
                       help='Run mode: single session, scheduled sessions, or test components')
    parser.add_argument('--max-applications', type=int, default=None,
                       help='Maximum applications for single session')
    parser.add_argument('--setup-resumes', type=str, default=None,
                       help='Path to base resume for creating specialized versions')
    parser.add_argument('--config', type=str, default='auto_apply_config.json',
                       help='Configuration file path')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = AutoApplyConfig(args.config)
        
        # Setup logging
        setup_logging(config)
        
        logger.info("🚀 LinkedIn Auto-Apply System Starting...")
        logger.info(f"Mode: {args.mode}")
        
        # Initialize orchestrator
        orchestrator = LinkedInAutoApplyOrchestrator(config)
        
        # Initialize components
        if not orchestrator.initialize_components():
            logger.error("❌ Failed to initialize components")
            sys.exit(1)
        
        # Setup resume versions if requested
        if args.setup_resumes:
            if orchestrator.setup_resume_versions(args.setup_resumes):
                logger.info("✅ Resume setup completed")
            else:
                logger.error("❌ Resume setup failed")
                sys.exit(1)
        
        # Run based on mode
        if args.mode == 'test':
            test_results = orchestrator.test_system_components()
            if test_results['overall_status']:
                logger.info("🎉 System test passed!")
                sys.exit(0)
            else:
                logger.error("❌ System test failed!")
                sys.exit(1)
        
        elif args.mode == 'single':
            results = orchestrator.run_single_session(args.max_applications)
            logger.info(f"✅ Session completed: {results['success_count']} applications submitted")
        
        elif args.mode == 'scheduled':
            orchestrator.run_scheduled_sessions()
        
    except KeyboardInterrupt:
        logger.info("⚠️ Process interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
    
    logger.info("👋 LinkedIn Auto-Apply System stopped")

if __name__ == "__main__":
    main()