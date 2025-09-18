#!/usr/bin/env python3
"""
Safety Manager for LinkedIn Auto-Apply
Implements safety measures, rate limiting, and anti-detection features
"""

import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path
import requests
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

logger = logging.getLogger(__name__)

@dataclass
class SafetyLimits:
    max_applications_per_day: int = 25
    max_applications_per_hour: int = 5
    max_applications_per_company: int = 2
    min_delay_between_applications: int = 45  # seconds
    max_delay_between_applications: int = 120  # seconds
    max_page_views_per_hour: int = 100
    max_search_queries_per_hour: int = 20
    cooldown_period_hours: int = 2  # Hours to wait if limits exceeded

@dataclass
class ActivityRecord:
    timestamp: str
    activity_type: str  # 'application', 'search', 'page_view', 'login'
    company: str = ""
    job_title: str = ""
    success: bool = True
    notes: str = ""

class SafetyManager:
    """Manages safety measures and rate limiting for LinkedIn automation"""
    
    def __init__(self, limits: SafetyLimits = None, db_path: str = "safety_tracking.db"):
        self.limits = limits or SafetyLimits()
        self.db_path = db_path
        self.session_start = datetime.now()
        self.last_activity = None
        self.activity_log = []
        
        # Initialize database
        self._init_database()
        
        # Load today's activity
        self._load_todays_activity()
        
        # Human-like behavior patterns
        self.human_patterns = {
            'typing_delays': (0.05, 0.15),  # seconds between keystrokes
            'mouse_movements': True,
            'scroll_behavior': True,
            'random_pauses': True
        }

    def _init_database(self):
        """Initialize SQLite database for activity tracking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    company TEXT DEFAULT '',
                    job_title TEXT DEFAULT '',
                    success BOOLEAN DEFAULT TRUE,
                    notes TEXT DEFAULT '',
                    date TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    date TEXT PRIMARY KEY,
                    applications_count INTEGER DEFAULT 0,
                    searches_count INTEGER DEFAULT 0,
                    page_views_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    companies_applied TEXT DEFAULT '[]'
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Safety database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing safety database: {e}")

    def _load_todays_activity(self):
        """Load today's activity from database"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, activity_type, company, job_title, success, notes
                FROM activities 
                WHERE date = ?
                ORDER BY timestamp
            ''', (today,))
            
            rows = cursor.fetchall()
            
            for row in rows:
                activity = ActivityRecord(
                    timestamp=row[0],
                    activity_type=row[1],
                    company=row[2],
                    job_title=row[3],
                    success=bool(row[4]),
                    notes=row[5]
                )
                self.activity_log.append(activity)
            
            conn.close()
            
            logger.info(f"Loaded {len(self.activity_log)} activities for today")
            
        except Exception as e:
            logger.error(f"Error loading today's activity: {e}")

    def record_activity(self, activity_type: str, company: str = "", 
                       job_title: str = "", success: bool = True, notes: str = ""):
        """Record an activity in the safety log"""
        try:
            activity = ActivityRecord(
                timestamp=datetime.now().isoformat(),
                activity_type=activity_type,
                company=company,
                job_title=job_title,
                success=success,
                notes=notes
            )
            
            self.activity_log.append(activity)
            self.last_activity = datetime.now()
            
            # Save to database
            self._save_activity_to_db(activity)
            
            # Update daily stats
            self._update_daily_stats()
            
        except Exception as e:
            logger.error(f"Error recording activity: {e}")

    def _save_activity_to_db(self, activity: ActivityRecord):
        """Save activity to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT INTO activities (timestamp, activity_type, company, job_title, success, notes, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (activity.timestamp, activity.activity_type, activity.company, 
                  activity.job_title, activity.success, activity.notes, today))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving activity to database: {e}")

    def _update_daily_stats(self):
        """Update daily statistics"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Calculate stats from today's activities
            applications = [a for a in self.activity_log if a.activity_type == 'application']
            searches = [a for a in self.activity_log if a.activity_type == 'search']
            page_views = [a for a in self.activity_log if a.activity_type == 'page_view']
            
            applications_count = len(applications)
            searches_count = len(searches)
            page_views_count = len(page_views)
            
            successful_applications = len([a for a in applications if a.success])
            success_rate = successful_applications / applications_count if applications_count > 0 else 0.0
            
            companies_applied = list(set([a.company for a in applications if a.company]))
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO daily_stats 
                (date, applications_count, searches_count, page_views_count, success_rate, companies_applied)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (today, applications_count, searches_count, page_views_count, 
                  success_rate, json.dumps(companies_applied)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating daily stats: {e}")

    def can_apply_to_job(self, company: str) -> Tuple[bool, str]:
        """Check if we can apply to a job based on safety limits"""
        now = datetime.now()
        
        # Check daily application limit
        todays_applications = [a for a in self.activity_log if a.activity_type == 'application']
        if len(todays_applications) >= self.limits.max_applications_per_day:
            return False, f"Daily application limit reached ({self.limits.max_applications_per_day})"
        
        # Check hourly application limit
        hour_ago = now - timedelta(hours=1)
        recent_applications = [a for a in self.activity_log 
                             if a.activity_type == 'application' and 
                             datetime.fromisoformat(a.timestamp) > hour_ago]
        
        if len(recent_applications) >= self.limits.max_applications_per_hour:
            return False, f"Hourly application limit reached ({self.limits.max_applications_per_hour})"
        
        # Check company-specific limit
        company_applications = [a for a in self.activity_log 
                              if a.activity_type == 'application' and a.company == company]
        
        if len(company_applications) >= self.limits.max_applications_per_company:
            return False, f"Company application limit reached for {company} ({self.limits.max_applications_per_company})"
        
        # Check minimum delay since last application
        if self.last_activity:
            time_since_last = (now - self.last_activity).total_seconds()
            if time_since_last < self.limits.min_delay_between_applications:
                return False, f"Minimum delay not met. Wait {self.limits.min_delay_between_applications - time_since_last:.0f} more seconds"
        
        return True, "OK"

    def can_perform_search(self) -> Tuple[bool, str]:
        """Check if we can perform a job search"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        recent_searches = [a for a in self.activity_log 
                         if a.activity_type == 'search' and 
                         datetime.fromisoformat(a.timestamp) > hour_ago]
        
        if len(recent_searches) >= self.limits.max_search_queries_per_hour:
            return False, f"Hourly search limit reached ({self.limits.max_search_queries_per_hour})"
        
        return True, "OK"

    def can_view_page(self) -> Tuple[bool, str]:
        """Check if we can view another page"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        recent_views = [a for a in self.activity_log 
                       if a.activity_type == 'page_view' and 
                       datetime.fromisoformat(a.timestamp) > hour_ago]
        
        if len(recent_views) >= self.limits.max_page_views_per_hour:
            return False, f"Hourly page view limit reached ({self.limits.max_page_views_per_hour})"
        
        return True, "OK"

    def get_next_application_delay(self) -> int:
        """Get the delay in seconds before next application"""
        base_delay = random.randint(self.limits.min_delay_between_applications, 
                                   self.limits.max_delay_between_applications)
        
        # Add some randomness based on recent activity
        recent_activity_count = len([a for a in self.activity_log 
                                   if datetime.fromisoformat(a.timestamp) > 
                                   datetime.now() - timedelta(minutes=30)])
        
        if recent_activity_count > 10:
            base_delay = int(base_delay * 1.5)  # Slow down if very active
        
        return base_delay

    def simulate_human_typing(self, element, text: str, driver):
        """Simulate human-like typing"""
        try:
            element.clear()
            
            for char in text:
                element.send_keys(char)
                delay = random.uniform(*self.human_patterns['typing_delays'])
                time.sleep(delay)
                
                # Occasional longer pauses (thinking)
                if random.random() < 0.1:
                    time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            logger.warning(f"Error in human typing simulation: {e}")
            element.send_keys(text)  # Fallback to normal typing

    def simulate_human_scrolling(self, driver):
        """Simulate human-like scrolling behavior"""
        try:
            if not self.human_patterns['scroll_behavior']:
                return
            
            # Random scroll pattern
            scroll_actions = [
                lambda: driver.execute_script("window.scrollBy(0, 300);"),
                lambda: driver.execute_script("window.scrollBy(0, -150);"),
                lambda: driver.execute_script("window.scrollBy(0, 500);"),
            ]
            
            action = random.choice(scroll_actions)
            action()
            
            time.sleep(random.uniform(0.5, 2.0))
            
        except Exception as e:
            logger.warning(f"Error in scroll simulation: {e}")

    def simulate_mouse_movements(self, driver):
        """Simulate random mouse movements"""
        try:
            if not self.human_patterns['mouse_movements']:
                return
            
            actions = ActionChains(driver)
            
            # Random mouse movements
            for _ in range(random.randint(1, 3)):
                x_offset = random.randint(-100, 100)
                y_offset = random.randint(-100, 100)
                
                actions.move_by_offset(x_offset, y_offset)
                actions.pause(random.uniform(0.1, 0.5))
            
            actions.perform()
            
        except Exception as e:
            logger.warning(f"Error in mouse movement simulation: {e}")

    def take_random_pause(self, context: str = ""):
        """Take a random pause to simulate human behavior"""
        if not self.human_patterns['random_pauses']:
            return
        
        # Different pause durations for different contexts
        pause_ranges = {
            'reading_job': (2, 8),
            'filling_form': (1, 4),
            'navigating': (0.5, 2),
            'default': (1, 3)
        }
        
        pause_range = pause_ranges.get(context, pause_ranges['default'])
        pause_duration = random.uniform(*pause_range)
        
        logger.debug(f"Taking {pause_duration:.1f}s pause ({context})")
        time.sleep(pause_duration)

    def detect_captcha_or_challenge(self, driver) -> bool:
        """Detect if LinkedIn is showing a CAPTCHA or security challenge"""
        try:
            challenge_indicators = [
                "captcha",
                "security check",
                "verify you're human",
                "unusual activity",
                "please verify",
                "challenge"
            ]
            
            page_source = driver.page_source.lower()
            
            for indicator in challenge_indicators:
                if indicator in page_source:
                    logger.warning(f"Security challenge detected: {indicator}")
                    return True
            
            # Check for specific elements
            challenge_elements = [
                "div[data-test-id='captcha']",
                ".challenge-page",
                "#captcha-internal",
                ".security-challenge"
            ]
            
            for selector in challenge_elements:
                try:
                    if driver.find_elements(By.CSS_SELECTOR, selector):
                        logger.warning(f"Challenge element found: {selector}")
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting challenges: {e}")
            return False

    def handle_rate_limiting(self, driver) -> bool:
        """Handle rate limiting by taking a break"""
        try:
            logger.warning("Rate limiting detected. Entering cooldown period...")
            
            # Record the rate limiting event
            self.record_activity(
                activity_type="rate_limit",
                notes=f"Cooldown for {self.limits.cooldown_period_hours} hours"
            )
            
            # Close browser to avoid detection
            if driver:
                driver.quit()
            
            # Calculate cooldown time
            cooldown_seconds = self.limits.cooldown_period_hours * 3600
            
            logger.info(f"Sleeping for {self.limits.cooldown_period_hours} hours...")
            time.sleep(cooldown_seconds)
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling rate limiting: {e}")
            return False

    def get_safety_report(self) -> Dict:
        """Generate a safety and activity report"""
        try:
            now = datetime.now()
            today = now.strftime('%Y-%m-%d')
            
            # Today's activities
            todays_activities = [a for a in self.activity_log]
            applications_today = [a for a in todays_activities if a.activity_type == 'application']
            searches_today = [a for a in todays_activities if a.activity_type == 'search']
            
            # Success rates
            successful_applications = [a for a in applications_today if a.success]
            success_rate = len(successful_applications) / len(applications_today) if applications_today else 0
            
            # Companies applied to
            companies_today = list(set([a.company for a in applications_today if a.company]))
            
            # Rate limit status
            can_apply, apply_reason = self.can_apply_to_job("")
            can_search, search_reason = self.can_perform_search()
            
            report = {
                'date': today,
                'session_duration_minutes': (now - self.session_start).total_seconds() / 60,
                'activities': {
                    'total': len(todays_activities),
                    'applications': len(applications_today),
                    'searches': len(searches_today),
                    'successful_applications': len(successful_applications)
                },
                'success_rate': success_rate,
                'companies_applied': companies_today,
                'limits_status': {
                    'can_apply': can_apply,
                    'apply_reason': apply_reason,
                    'can_search': can_search,
                    'search_reason': search_reason,
                    'applications_remaining': max(0, self.limits.max_applications_per_day - len(applications_today))
                },
                'safety_metrics': {
                    'avg_delay_between_applications': self._calculate_avg_delay(),
                    'peak_activity_hour': self._get_peak_activity_hour(),
                    'rate_limit_events': len([a for a in todays_activities if a.activity_type == 'rate_limit'])
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating safety report: {e}")
            return {}

    def _calculate_avg_delay(self) -> float:
        """Calculate average delay between applications"""
        applications = [a for a in self.activity_log if a.activity_type == 'application']
        
        if len(applications) < 2:
            return 0.0
        
        delays = []
        for i in range(1, len(applications)):
            prev_time = datetime.fromisoformat(applications[i-1].timestamp)
            curr_time = datetime.fromisoformat(applications[i].timestamp)
            delay = (curr_time - prev_time).total_seconds()
            delays.append(delay)
        
        return sum(delays) / len(delays) if delays else 0.0

    def _get_peak_activity_hour(self) -> int:
        """Get the hour with most activity"""
        hour_counts = {}
        
        for activity in self.activity_log:
            hour = datetime.fromisoformat(activity.timestamp).hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        if not hour_counts:
            return 0
        
        return max(hour_counts.items(), key=lambda x: x[1])[0]

    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old activity data"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime('%Y-%m-%d')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete old activities
            cursor.execute('DELETE FROM activities WHERE date < ?', (cutoff_date,))
            cursor.execute('DELETE FROM daily_stats WHERE date < ?', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted_count} old activity records")
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

class LinkedInDetectionAvoidance:
    """Advanced techniques to avoid LinkedIn's automation detection"""
    
    def __init__(self, driver):
        self.driver = driver
        
    def setup_stealth_mode(self):
        """Configure browser to avoid detection"""
        try:
            # Execute stealth JavaScript
            stealth_script = """
            // Override webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Mock chrome runtime
            window.chrome = {
                runtime: {}
            };
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            """
            
            self.driver.execute_script(stealth_script)
            
        except Exception as e:
            logger.warning(f"Error setting up stealth mode: {e}")
    
    def randomize_viewport_size(self):
        """Randomize browser viewport size"""
        try:
            widths = [1366, 1440, 1536, 1920]
            heights = [768, 900, 1024, 1080]
            
            width = random.choice(widths)
            height = random.choice(heights)
            
            self.driver.set_window_size(width, height)
            
        except Exception as e:
            logger.warning(f"Error randomizing viewport: {e}")
    
    def simulate_real_user_behavior(self):
        """Simulate various real user behaviors"""
        try:
            behaviors = [
                self._simulate_tab_switching,
                self._simulate_back_forward,
                self._simulate_zoom_change,
                self._simulate_dev_tools_check
            ]
            
            # Randomly execute some behaviors
            for behavior in random.sample(behaviors, k=random.randint(1, 3)):
                try:
                    behavior()
                except:
                    continue
                    
        except Exception as e:
            logger.warning(f"Error simulating user behavior: {e}")
    
    def _simulate_tab_switching(self):
        """Simulate switching between tabs"""
        # Open a new tab briefly
        self.driver.execute_script("window.open('about:blank', '_blank');")
        time.sleep(random.uniform(1, 3))
        
        # Switch back to main tab
        self.driver.switch_to.window(self.driver.window_handles[0])
        
        # Close the extra tab if it exists
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
    
    def _simulate_back_forward(self):
        """Simulate using back/forward buttons"""
        if random.random() < 0.3:  # 30% chance
            self.driver.back()
            time.sleep(random.uniform(1, 2))
            self.driver.forward()
    
    def _simulate_zoom_change(self):
        """Simulate changing zoom level"""
        zoom_levels = [0.8, 0.9, 1.0, 1.1, 1.25]
        zoom = random.choice(zoom_levels)
        self.driver.execute_script(f"document.body.style.zoom='{zoom}'")
    
    def _simulate_dev_tools_check(self):
        """Simulate checking if dev tools are open"""
        self.driver.execute_script("""
            // Check dev tools
            let devtools = {open: false, orientation: null};
            setInterval(() => {
                if (window.outerHeight - window.innerHeight > 200) {
                    devtools.open = true;
                    devtools.orientation = 'vertical';
                }
            }, 500);
        """)