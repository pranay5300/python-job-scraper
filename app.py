from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import aiohttp
import asyncio
import os
import random
import time

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Directory for temporary file storage
TEMP_DIR = "temp_files"
os.makedirs(TEMP_DIR, exist_ok=True)

# Function to scrape LinkedIn jobs asynchronously
async def scrape_linkedin_jobs(session, company, role, location, job_type, page=1):
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

        async with session.get(search_url, headers=headers, timeout=15) as response:
            if response.status != 200:
                print(f"Failed to fetch LinkedIn page: {response.status}")
                return []

            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

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

                except Exception as e:
                    print(f"Error parsing job card: {e}")
                    continue

            return jobs
    except Exception as e:
        print(f"Error scraping LinkedIn: {e}")
        return []

# Function to calculate job match scores
def rank_jobs(jobs, companies, roles, locations, overall_company_weight, overall_role_weight, overall_location_weight):
    def calculate_score(job):
        company_score = sum(
            (1 if c["company"].lower() in job["Company Name"].lower() else 0) * (c["weight"] / 100)
            for c in companies
        )

        role_score = sum(
            (1 if r["role"].lower() in job["Job Title"].lower() else 0) * (r["weight"] / 100)
            for r in roles
        )

        location_score = sum(
            (1 if l["location"].lower() in job["Location"].lower() else 0) * (l["weight"] / 100)
            for l in locations
        )

        return (
            overall_company_weight * company_score +
            overall_role_weight * role_score +
            overall_location_weight * location_score
        )

    # Add a score to each job and sort by score
    for job in jobs:
        job["Score"] = calculate_score(job)

    return sorted(jobs, key=lambda x: x["Score"], reverse=True)

# API endpoint to generate and download Excel
@app.route('/download_excel', methods=['GET'])
async def download_excel():
    try:
        # Extract query parameters
        companies = request.args.get("companies", [])
        roles = request.args.get("roles", [])
        locations = request.args.get("locations", [])
        overall_company_weight = float(request.args.get("overall_company_weight", 0)) / 100
        overall_role_weight = float(request.args.get("overall_role_weight", 0)) / 100
        overall_location_weight = float(request.args.get("overall_location_weight", 0)) / 100

        # Validate inputs
        if overall_company_weight + overall_role_weight + overall_location_weight != 1:
            return jsonify({"error": "Overall weights must sum up to 100."}), 400

        # Convert stringified JSON parameters to Python lists
        companies = eval(companies)
        roles = eval(roles)
        locations = eval(locations)

        # Prepare an async session for scraping
        async with aiohttp.ClientSession() as session:
            tasks = []
            for company in companies:
                for role in roles:
                    for location in locations:
                        tasks.append(scrape_linkedin_jobs(session, company["company"], role["role"], location["location"], ""))

            results = await asyncio.gather(*tasks)

        # Flatten the results and remove duplicates
        unique_jobs = {tuple(job.items()): job for job_list in results for job in job_list}.values()

        # Rank jobs based on scores
        ranked_jobs = rank_jobs(
            list(unique_jobs), companies, roles, locations,
            overall_company_weight, overall_role_weight, overall_location_weight
        )

        # Save job data to Excel
        df = pd.DataFrame(ranked_jobs)
        file_path = os.path.join(TEMP_DIR, "job_data.xlsx")
        df.to_excel(file_path, index=False)

        # Return the Excel file
        return send_file(file_path, as_attachment=True, download_name="job_data.xlsx")
    except Exception as e:
        print(f"Error generating Excel: {e}")
        return jsonify({"error": f"Error generating Excel: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
