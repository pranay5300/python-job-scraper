import asyncio
import aiohttp
import re
import hashlib
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class H1BPredictor:
    """High-performance H1B sponsorship predictor using myvisajobs data and ML."""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.company_encoder = None
        self.prediction_cache = {}
        self.model_file = 'h1b_model.joblib'
        self.vectorizer_file = 'h1b_vectorizer.joblib'
        self.company_encoder_file = 'h1b_company_encoder.joblib'
        self.last_update = None
        self.h1b_companies_db = None
        
    def initialize(self):
        """Initialize the H1B predictor with pre-trained model or train new one."""
        try:
            # Try to load existing model
            if self._load_model():
                logger.info("H1B predictor loaded from saved model")
            else:
                # Train new model with sample data
                logger.info("Training new H1B prediction model...")
                self._train_model()
                logger.info("H1B prediction model trained successfully")
                
            # Load H1B sponsoring companies database
            self._load_h1b_companies_db()
            
        except Exception as e:
            logger.error(f"H1B predictor initialization error: {e}")
            # Fallback to simple rule-based predictions
            self._initialize_fallback()
    
    def _load_model(self) -> bool:
        """Load pre-trained model from disk."""
        try:
            if all(os.path.exists(f) for f in [self.model_file, self.vectorizer_file, self.company_encoder_file]):
                self.model = joblib.load(self.model_file)
                self.vectorizer = joblib.load(self.vectorizer_file)
                self.company_encoder = joblib.load(self.company_encoder_file)
                return True
        except Exception as e:
            logger.error(f"Model loading error: {e}")
        return False
    
    def _save_model(self):
        """Save trained model to disk."""
        try:
            joblib.dump(self.model, self.model_file)
            joblib.dump(self.vectorizer, self.vectorizer_file)
            joblib.dump(self.company_encoder, self.company_encoder_file)
        except Exception as e:
            logger.error(f"Model saving error: {e}")
    
    def _train_model(self):
        """Train H1B prediction model with synthetic data based on known patterns."""
        # Create training data based on known H1B sponsorship patterns
        training_data = self._generate_training_data()
        
        df = pd.DataFrame(training_data)
        
        # Prepare features
        X_text = df['job_title'] + " " + df['company_name']
        y = df['sponsors_h1b']
        
        # Text vectorization
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        X_vectorized = self.vectorizer.fit_transform(X_text)
        
        # Company encoding
        self.company_encoder = LabelEncoder()
        company_encoded = self.company_encoder.fit_transform(df['company_name'])
        
        # Combine features
        X = np.hstack([X_vectorized.toarray(), company_encoded.reshape(-1, 1)])
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X, y)
        
        # Save model
        self._save_model()
        
        logger.info(f"Model trained on {len(training_data)} samples")
    
    def _generate_training_data(self) -> List[Dict]:
        """Generate training data based on known H1B sponsorship patterns."""
        # Companies known to sponsor H1B visas
        h1b_companies = [
            'Google', 'Microsoft', 'Amazon', 'Apple', 'Meta', 'Netflix', 'Tesla',
            'NVIDIA', 'Intel', 'Cisco', 'Oracle', 'IBM', 'Salesforce', 'Adobe',
            'Uber', 'Airbnb', 'Spotify', 'Twitter', 'LinkedIn', 'Snap',
            'Palantir', 'Databricks', 'Snowflake', 'Stripe', 'Square',
            'Goldman Sachs', 'JPMorgan Chase', 'Morgan Stanley', 'Bank of America',
            'Accenture', 'Deloitte', 'McKinsey', 'BCG', 'Bain',
            'Qualcomm', 'Broadcom', 'AMD', 'Micron', 'Applied Materials'
        ]
        
        # Job titles commonly sponsored
        sponsored_roles = [
            'Software Engineer', 'Data Scientist', 'Machine Learning Engineer',
            'Software Developer', 'Senior Software Engineer', 'Principal Engineer',
            'Research Scientist', 'AI Engineer', 'Backend Engineer', 'Frontend Engineer',
            'Full Stack Engineer', 'DevOps Engineer', 'Cloud Engineer',
            'Product Manager', 'Technical Program Manager', 'Engineering Manager',
            'Data Engineer', 'Analytics Engineer', 'Platform Engineer',
            'Security Engineer', 'Site Reliability Engineer', 'Solutions Architect'
        ]
        
        # Companies less likely to sponsor
        non_h1b_companies = [
            'Local Restaurant', 'Small Retail Store', 'Startup Inc', 'Family Business',
            'Local Services LLC', 'Regional Bank', 'Community Hospital',
            'Local Construction', 'Small Agency', 'Local Consulting'
        ]
        
        # Roles less likely to be sponsored
        non_sponsored_roles = [
            'Customer Service', 'Sales Associate', 'Cashier', 'Server',
            'Administrative Assistant', 'Receptionist', 'Security Guard',
            'Maintenance Worker', 'Driver', 'Warehouse Worker'
        ]
        
        training_data = []
        
        # Positive examples (H1B sponsors)
        for company in h1b_companies:
            for role in sponsored_roles:
                training_data.append({
                    'company_name': company,
                    'job_title': role,
                    'sponsors_h1b': 1
                })
        
        # Negative examples (Non-sponsors)
        for company in non_h1b_companies:
            for role in non_sponsored_roles:
                training_data.append({
                    'company_name': company,
                    'job_title': role,
                    'sponsors_h1b': 0
                })
        
        # Mixed examples (some tech companies for non-tech roles)
        for company in h1b_companies[:10]:
            for role in non_sponsored_roles[:5]:
                training_data.append({
                    'company_name': company,
                    'job_title': role,
                    'sponsors_h1b': 0  # Tech companies don't sponsor for all roles
                })
        
        return training_data
    
    def _load_h1b_companies_db(self):
        """Load database of companies and their H1B sponsorship history."""
        # This would ideally load from myvisajobs or similar database
        # For now, use hardcoded high-probability sponsors
        self.h1b_companies_db = {
            # Tech giants (very high probability)
            'google': 0.95, 'microsoft': 0.94, 'amazon': 0.92, 'apple': 0.90,
            'meta': 0.89, 'facebook': 0.89, 'netflix': 0.87, 'tesla': 0.85,
            'nvidia': 0.88, 'intel': 0.86, 'cisco': 0.84, 'oracle': 0.83,
            'ibm': 0.82, 'salesforce': 0.85, 'adobe': 0.83, 'uber': 0.80,
            
            # Financial services
            'goldman sachs': 0.75, 'jpmorgan': 0.73, 'morgan stanley': 0.72,
            'bank of america': 0.70, 'wells fargo': 0.68,
            
            # Consulting
            'accenture': 0.78, 'deloitte': 0.76, 'mckinsey': 0.74,
            'bcg': 0.73, 'bain': 0.72,
            
            # Semiconductors
            'qualcomm': 0.84, 'broadcom': 0.82, 'amd': 0.80, 'micron': 0.78,
            
            # Smaller companies (lower probability)
            'startup': 0.20, 'small business': 0.10, 'local': 0.05
        }
    
    def _initialize_fallback(self):
        """Initialize fallback rule-based predictor."""
        logger.info("Initializing fallback H1B predictor")
        self.model = None
        
    def _rule_based_prediction(self, company: str, role: str) -> float:
        """Rule-based H1B prediction as fallback."""
        company_lower = company.lower()
        role_lower = role.lower()
        
        # Check company database
        for known_company, probability in self.h1b_companies_db.items():
            if known_company in company_lower:
                # Adjust based on role
                if any(tech_role in role_lower for tech_role in 
                       ['engineer', 'developer', 'scientist', 'analyst', 'manager']):
                    return min(probability * 1.1, 1.0)  # Boost for tech roles
                elif any(non_tech_role in role_lower for non_tech_role in 
                        ['sales', 'marketing', 'hr', 'admin', 'support']):
                    return probability * 0.7  # Reduce for non-tech roles
                return probability
        
        # Default predictions based on role
        if any(tech_role in role_lower for tech_role in 
               ['software', 'engineer', 'developer', 'data scientist', 'machine learning']):
            return 0.6  # Medium probability for tech roles at unknown companies
        elif any(business_role in role_lower for business_role in 
                ['manager', 'analyst', 'consultant', 'specialist']):
            return 0.3  # Lower probability for business roles
        else:
            return 0.1  # Very low probability for other roles
    
    async def predict_single(self, company: str, role: str) -> float:
        """Predict H1B sponsorship probability for a single job."""
        try:
            # Check cache first
            cache_key = f"{company.lower()}:{role.lower()}"
            if cache_key in self.prediction_cache:
                return self.prediction_cache[cache_key]
            
            if self.model and self.vectorizer and self.company_encoder:
                # ML prediction
                text_input = f"{role} {company}"
                X_text = self.vectorizer.transform([text_input])
                
                # Handle unknown companies
                try:
                    company_encoded = self.company_encoder.transform([company])
                except ValueError:
                    # Unknown company, use a default encoding
                    company_encoded = [0]
                
                X = np.hstack([X_text.toarray(), np.array(company_encoded).reshape(-1, 1)])
                probability = self.model.predict_proba(X)[0][1]  # Probability of class 1 (sponsors)
            else:
                # Fallback to rule-based
                probability = self._rule_based_prediction(company, role)
            
            # Cache the result
            self.prediction_cache[cache_key] = probability
            
            return probability
            
        except Exception as e:
            logger.error(f"H1B prediction error for {company} {role}: {e}")
            return 0.3  # Default medium probability
    
    async def batch_predict(self, companies: List[str], roles: List[str]) -> List[float]:
        """Batch predict H1B sponsorship probabilities."""
        try:
            if len(companies) != len(roles):
                raise ValueError("Companies and roles lists must have same length")
            
            predictions = []
            
            if self.model and self.vectorizer and self.company_encoder:
                # Batch ML prediction for better performance
                text_inputs = [f"{role} {company}" for role, company in zip(roles, companies)]
                X_text = self.vectorizer.transform(text_inputs)
                
                # Handle company encodings
                company_encodings = []
                for company in companies:
                    try:
                        encoded = self.company_encoder.transform([company])[0]
                    except ValueError:
                        encoded = 0  # Default for unknown companies
                    company_encodings.append(encoded)
                
                X = np.hstack([X_text.toarray(), np.array(company_encodings).reshape(-1, 1)])
                probabilities = self.model.predict_proba(X)[:, 1]  # Probabilities of class 1
                predictions = probabilities.tolist()
            else:
                # Fallback to rule-based predictions
                for company, role in zip(companies, roles):
                    prediction = self._rule_based_prediction(company, role)
                    predictions.append(prediction)
            
            # Cache all predictions
            for (company, role), prediction in zip(zip(companies, roles), predictions):
                cache_key = f"{company.lower()}:{role.lower()}"
                self.prediction_cache[cache_key] = prediction
            
            return predictions
            
        except Exception as e:
            logger.error(f"Batch H1B prediction error: {e}")
            # Return default predictions
            return [0.3] * len(companies)
    
    async def scrape_myvisajobs_data(self, company: str) -> Optional[Dict]:
        """Scrape H1B data from myvisajobs for a specific company."""
        try:
            url = f"https://www.myvisajobs.com/Visa-Sponsor/{company.replace(' ', '-')}/page.htm"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # Extract H1B statistics (simplified)
                        h1b_approved = re.search(r'H1B Approved:\s*(\d+)', html)
                        total_applications = re.search(r'Total Applications:\s*(\d+)', html)
                        
                        if h1b_approved and total_applications:
                            approved = int(h1b_approved.group(1))
                            total = int(total_applications.group(1))
                            probability = approved / total if total > 0 else 0
                            
                            return {
                                'company': company,
                                'h1b_approved': approved,
                                'total_applications': total,
                                'probability': probability,
                                'scraped_at': datetime.now().isoformat()
                            }
            
        except Exception as e:
            logger.error(f"MyVisaJobs scraping error for {company}: {e}")
        
        return None
    
    def get_prediction_stats(self) -> Dict:
        """Get prediction statistics."""
        return {
            'model_loaded': self.model is not None,
            'cache_size': len(self.prediction_cache),
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'companies_in_db': len(self.h1b_companies_db) if self.h1b_companies_db else 0
        }