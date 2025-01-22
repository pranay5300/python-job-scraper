from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random
import json

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Function to scrape LinkedIn jobs
def scrape_linkedin_jobs(company, role, location, job_type, page=1):
    try:
        keywords = f"{role} {company} {job_type}"
        params = {
            'keywords': keywords,
            'location': location,
            'start': (page - 1) * 25,
            'trk': 'public_jobs_jobs-search-bar_search-submit'
        }
        search_url = "https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(params)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(search_url, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"Failed to fetch LinkedIn page: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')

        # Parse job cards
        job_cards = soup.find_all('div', class_='base-search-card')
        jobs = []
        for card in job_cards:
            try:
                title_elem = card.find('h3', class_='base-search-card__title')
                company_elem = card.find('h4', class_='base-search-card__subtitle')
                location_elem = card.find('span', class_='job-search-card__location')
                link_elem = card.find('a', class_='base-card__full-link')

                jobs.append({
                    "Job Title": title_elem.get_text(strip=True) if title_elem else "N/A",
                    "Company Name": company_elem.get_text(strip=True) if company_elem else "N/A",
                    "Location": location_elem.get_text(strip=True) if location_elem else "N/A",
                    "Job Link": link_elem['href'].strip() if link_elem else "N/A"
                })

                # Introduce a delay to avoid being flagged
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"Error parsing job card: {e}")
                continue

        return jobs
    except Exception as e:
        print(f"Error scraping LinkedIn: {e}")
        return []

# Function to calculate job match scores
def rank_jobs(jobs, roles, companies, locations, overall_weights):
    def calculate_score(job):
        # Compute role, company, and location scores
        role_score = sum(weight for role, weight in roles if role.lower() in job["Job Title"].lower())
        company_score = sum(weight for company, weight in companies if company.lower() in job["Company Name"].lower())
        location_score = sum(weight for location, weight in locations if location.lower() in job["Location"].lower())

        # Weighted score
        score = (
            overall_weights["role_weight"] * role_score +
            overall_weights["company_weight"] * company_score +
            overall_weights["location_weight"] * location_score
        )
        return score

    # Add a score to each job and sort by score
    for job in jobs:
        job["Score"] = calculate_score(job)

    return sorted(jobs, key=lambda x: x["Score"], reverse=True)

# API endpoint to generate and download Excel
@app.route('/download_excel', methods=['GET'])
def download_excel():
    try:
        # Extract query parameters
        roles = json.loads(request.args.get("roles", "[]"))
        companies = json.loads(request.args.get("companies", "[]"))
        locations = json.loads(request.args.get("locations", "[]"))
        overall_weights = {
            "company_weight": float(request.args.get("overall_company_weight", 0)),
            "role_weight": float(request.args.get("overall_role_weight", 0)),
            "location_weight": float(request.args.get("overall_location_weight", 0))
        }

        # Convert sub-weights to floats with error handling
        try:
            roles = [(role["role"], float(role["weight"])) for role in roles]
            companies = [(company["company"], float(company["weight"])) for company in companies]
            locations = [(location["location"], float(location["weight"])) for location in locations]
        except ValueError as e:
            return jsonify({"error": f"Invalid weight format. All weights must be numeric. Details: {str(e)}"}), 400

        # Validate overall weights sum to 100
        if sum(overall_weights.values()) != 100:
            return jsonify({"error": "Overall weights for companies, roles, and locations must sum to 100%."}), 400

        # Validate sub-weights sum to 100 for each category
        if sum([weight for _, weight in roles]) != 100 or \
           sum([weight for _, weight in companies]) != 100 or \
           sum([weight for _, weight in locations]) != 100:
            return jsonify({"error": "Sub-weights for companies, roles, and locations must each sum to 100%."}), 400

        # Scrape jobs for all combinations
        all_jobs = []
        for company, _ in companies:
            for role, _ in roles:
                for location, _ in locations:
                    jobs = scrape_linkedin_jobs(company, role, location, job_type="")
                    all_jobs.extend(jobs)

        # Remove duplicates
        unique_jobs = [dict(t) for t in {tuple(d.items()) for d in all_jobs}]

        # Rank jobs based on weights
        ranked_jobs = rank_jobs(unique_jobs, roles, companies, locations, overall_weights)

        # Save job data to Excel
        df = pd.DataFrame(ranked_jobs)
        file_path = "job_data.xlsx"
        df.to_excel(file_path, index=False)

        # Return the Excel file
        return send_file(file_path, as_attachment=True, download_name="job_data.xlsx")
    except Exception as e:
        return jsonify({"error": f"Error generating Excel: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
