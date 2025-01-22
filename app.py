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

# Function to rank jobs based on weights
def rank_jobs(jobs, roles, companies, locations):
    def calculate_score(job):
        role_score = max(
            (weight for role, weight in roles if role.lower() in job["Job Title"].lower()),
            default=0
        )
        company_score = max(
            (weight for company, weight in companies if company.lower() in job["Company Name"].lower()),
            default=0
        )
        location_score = max(
            (weight for location, weight in locations if location.lower() in job["Location"].lower()),
            default=0
        )

        # Total weighted score
        return role_score + company_score + location_score

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

        # Validate that weights sum up to 100 for each category
        role_weights = [weight for _, weight in roles]
        company_weights = [weight for _, weight in companies]
        location_weights = [weight for _, weight in locations]

        if sum(role_weights) != 100 or sum(company_weights) != 100 or sum(location_weights) != 100:
            return jsonify({"error": "Weights for roles, companies, and locations must each sum up to 100%."}), 400

        # Scrape jobs for all combinations
        all_jobs = []
        for company, company_weight in companies:
            for role, role_weight in roles:
                for location, location_weight in locations:
                    jobs = scrape_linkedin_jobs(company, role, location, job_type="")
                    all_jobs.extend(jobs)

        # Remove duplicates
        unique_jobs = [dict(t) for t in {tuple(d.items()) for d in all_jobs}]

        # Rank jobs based on weights
        ranked_jobs = rank_jobs(unique_jobs, roles, companies, locations)

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

