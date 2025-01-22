from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
import json
import requests
from bs4 import BeautifulSoup
import time
import random

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Function to scrape LinkedIn jobs
def scrape_linkedin_jobs(company, role, location, job_type):
    try:
        base_url = "https://www.linkedin.com/jobs/search/"
        params = {
            'keywords': f"{role} {company} {job_type}",
            'location': location,
            'trk': 'public_jobs_jobs-search-bar_search-submit'
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(base_url, params=params, headers=headers, timeout=15)

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
                time.sleep(random.uniform(1, 2))
            except Exception as e:
                print(f"Error parsing job card: {e}")
                continue

        return jobs
    except Exception as e:
        print(f"Error scraping LinkedIn: {e}")
        return []

# Function to calculate job match scores
def rank_jobs(jobs, weights, role, location, company):
    def calculate_score(job):
        # Scoring based on matches
        company_match = 1 if company.lower() in job["Company Name"].lower() else 0
        role_match = 1 if role.lower() in job["Job Title"].lower() else 0
        location_match = 1 if location.lower() in job["Location"].lower() else 0

        # Weighted score
        return (
            company_match * weights["company_weight"] +
            role_match * weights["role_weight"] +
            location_match * weights["location_weight"]
        )

    # Add scores to jobs and sort by score
    for job in jobs:
        job["Score"] = calculate_score(job)

    return sorted(jobs, key=lambda x: x["Score"], reverse=True)

# API endpoint to generate and download Excel
@app.route('/download_excel', methods=['GET'])
def download_excel():
    try:
        # Extract query parameters
        companies = json.loads(request.args.get("companies", "[]"))
        roles = json.loads(request.args.get("roles", "[]"))
        locations = json.loads(request.args.get("locations", "[]"))
        overall_company_weight = float(request.args.get("overall_company_weight", 0))
        overall_role_weight = float(request.args.get("overall_role_weight", 0))
        overall_location_weight = float(request.args.get("overall_location_weight", 0))

        # Validate overall weights
        total_weight = overall_company_weight + overall_role_weight + overall_location_weight
        if total_weight != 100:
            return jsonify({"error": f"Overall weights must sum up to 100%. Current total: {total_weight}"}), 400

        # Normalize weights
        weights = {
            "company_weight": overall_company_weight / 100,
            "role_weight": overall_role_weight / 100,
            "location_weight": overall_location_weight / 100
        }

        # Validate individual weights for companies, roles, and locations
        for entity_list, entity_name in zip([companies, roles, locations], ["companies", "roles", "locations"]):
            entity_total_weight = sum(float(e.get("weight", 0)) for e in entity_list)
            if entity_total_weight != 100:
                return jsonify({"error": f"{entity_name.capitalize()} weights must sum up to 100%. Current total: {entity_total_weight}"}), 400

        # Aggregate all jobs
        all_jobs = []
        for company in companies:
            for role in roles:
                for location in locations:
                    scraped_jobs = scrape_linkedin_jobs(company["company"], role["role"], location["location"], "full-time")
                    all_jobs.extend(scraped_jobs)

        # Check if jobs were found
        if not all_jobs:
            return jsonify({"error": "No jobs found"}), 404

        # Rank jobs based on weights
        ranked_jobs = rank_jobs(all_jobs, weights, roles[0]["role"], locations[0]["location"], companies[0]["company"])

        # Save job data to Excel
        file_path = "job_data.xlsx"
        df = pd.DataFrame(ranked_jobs)
        df.to_excel(file_path, index=False)

        # Return the Excel file
        return send_file(file_path, as_attachment=True, download_name="job_data.xlsx")
    except Exception as e:
        return jsonify({"error": f"Error processing request: {str(e)}"}), 500
    finally:
        # Cleanup the generated file
        if os.path.exists("job_data.xlsx"):
            os.remove("job_data.xlsx")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
