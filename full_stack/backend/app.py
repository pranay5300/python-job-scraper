from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
import json
from fuzzywuzzy import fuzz
import time
import random
from bs4 import BeautifulSoup
import requests
import uuid
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from openpyxl import Workbook

app = Flask(__name__)
CORS(app)

# Configuration
MAX_RESULTS = 30
REQUEST_TIMEOUT = 10
DELAY_RANGE = (1, 3)
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
]

# USCIS Google Sheet setup
H1B_SHEET_URL = "https://docs.google.com/spreadsheets/d/1-pnpCHYRfWLuqFucvv_ryTkhZDR1LRJN/export?format=csv"
REQUIRED_COLUMNS = ['Company', 'Role', 'H1b Approval 2024', 'H1b Sponsor']

@lru_cache(maxsize=128)
def scrape_linkedin_jobs_cached(company, role, location, job_type):
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        params = {
            'keywords': f"{role} {company} {job_type}",
            'location': location,
            'trk': 'public_jobs_jobs-search-bar_search-submit',
            'count': 10
        }

        response = requests.get(
            "https://www.linkedin.com/jobs/search/",
            params=params,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        return parse_job_cards(soup)
        
    except Exception as e:
        app.logger.error(f"Scraping Error: {e}")
        return []

@lru_cache(maxsize=128)
def scrape_linkedin_jobs(company, role, location, job_type):
    return scrape_linkedin_jobs_cached(company, role, location, job_type)

def parse_job_cards(soup):
    jobs = []
    for card in soup.find_all('div', {'class': 'base-search-card'}):
        try:
            jobs.append({
                "Job Title": card.find('h3', class_='base-search-card__title').get_text(strip=True),
                "Company Name": card.find('h4', class_='base-search-card__subtitle').get_text(strip=True),
                "Location": card.find('span', class_='job-search-card__location').get_text(strip=True),
                "Job Link": card.find('a', class_='base-card__full-link')['href'].strip()
            })
        except AttributeError:
            continue
        time.sleep(random.uniform(*DELAY_RANGE))
    return jobs

def embed_job_links(jobs):
    for job in jobs:
        job_title = job['Job Title']
        job_link = job.pop('Job Link')  # Remove and use for hyperlink
        job['Job Title'] = f'=HYPERLINK("{job_link}", "{job_title}")'
    return jobs

def calculate_score(job, companies, roles, locations, weights):
    company_score = max(
        (float(company["weight"])/100 if company["company"].lower() in job["Company Name"].lower() else 0
        ) for company in companies
    )
    role_score = max(
        (float(role["weight"])/100 if role["role"].lower() in job["Job Title"].lower() else 0
        ) for role in roles
    )
    location_score = max(
        (float(location["weight"])/100 if location["location"].lower() in job["Location"].lower() else 0
        ) for location in locations
    )
    return (company_score * weights["company_weight"] +
            role_score * weights["role_weight"] +
            location_score * weights["location_weight"])

def rank_jobs(jobs, companies, roles, locations, weights):
    for job in jobs:
        job["Score"] = calculate_score(job, companies, roles, locations, weights)
    return sorted(jobs, key=lambda x: x["Score"], reverse=True)

def get_h1b_data_for_company(company, role):
    try:
        if not hasattr(get_h1b_data_for_company, 'h1b_df'):
            h1b_df = pd.read_csv(H1B_SHEET_URL)
            h1b_df = h1b_df[REQUIRED_COLUMNS].dropna()
            get_h1b_data_for_company.h1b_df = h1b_df
            
        # First try exact company match
        company_matches = get_h1b_data_for_company.h1b_df[
            get_h1b_data_for_company.h1b_df['Company'].str.lower() == company.lower()
        ]
        
        # If no exact match, try fuzzy matching
        if company_matches.empty:
            best_match = None
            best_score = 0
            
            for _, row in get_h1b_data_for_company.h1b_df.iterrows():
                company_score = fuzz.token_set_ratio(str(company).lower(), str(row['Company']).lower())
                
                # Lower threshold for company match only
                if company_score > 70:  # Adjusted threshold
                    if best_score < company_score:
                        best_match = row
                        best_score = company_score
        else:
            best_match = company_matches.iloc[0]
            
        return {
            "H1b Approval 2024": best_match['H1b Approval 2024'] if best_match is not None else "N/A",
            "H1b Sponsor": best_match['H1b Sponsor'] if best_match is not None else "No"
        }
        
    except Exception as e:
        app.logger.error(f"H1B Data Error: {e}")
        return {"H1b Approval 2024": "N/A", "H1b Sponsor": "No"}

def create_excel_with_sorting(jobs, file_path):
    """Create Excel file with sorting/filtering headers"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Job Data"
    
    # Create headers
    headers = [
        'Job Title', 'Company Name', 'Location',
        'H1b Approval 2024', 'H1b Sponsor', 'Score'
    ]
    ws.append(headers)
    
    # Add data rows
    for job in jobs:
        ws.append([
            job['Job Title'],        # Contains HYPERLINK formula
            job['Company Name'],
            job['Location'],
            job['H1b Approval 2024'],
            job['H1b Sponsor'],
            job['Score']
        ])
    
    # Enable sorting/filtering arrows
    ws.auto_filter.ref = ws.dimensions
    wb.save(file_path)

@app.route('/download_excel', methods=['GET'])
def download_excel():
    try:
        # Parse and validate inputs
        companies = json.loads(request.args.get("companies", "[]"))
        roles = json.loads(request.args.get("roles", "[]"))
        locations = json.loads(request.args.get("locations", "[]"))
        weights = {
            "company_weight": float(request.args.get("overall_company_weight", 33))/100,
            "role_weight": float(request.args.get("overall_role_weight", 33))/100,
            "location_weight": float(request.args.get("overall_location_weight", 34))/100
        }

        # Validate weights
        if abs(sum(weights.values()) - 1.0) > 0.001:  # Allow floating point precision
            return jsonify({"error": "Weights must sum to 100%"}), 400

        # Scrape jobs in parallel
        all_jobs = []
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(scrape_linkedin_jobs, 
                              company["company"], 
                              role["role"], 
                              location["location"],
                              "Full-Time")
                for company in companies
                for role in roles
                for location in locations
            ]
            for future in futures:
                all_jobs.extend(future.result())

        if not all_jobs:
            return jsonify({"error": "No jobs found"}), 404

        # Rank and select top jobs
        ranked_jobs = rank_jobs(all_jobs, companies, roles, locations, weights)[:MAX_RESULTS]

        # Add H1B data and process links
        for job in ranked_jobs:
            job.update(get_h1b_data_for_company(job["Company Name"], job["Job Title"]))
        ranked_jobs = embed_job_links(ranked_jobs)

        # Generate Excel with sorting
        file_path = f"job_data_{uuid.uuid4()}.xlsx"
        create_excel_with_sorting(ranked_jobs, file_path)

        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        app.logger.error(f"Critical Error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
