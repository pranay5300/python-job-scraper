import asyncio
import aiohttp
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
from bs4 import BeautifulSoup
import urllib.parse
import json

app = Flask(__name__)
CORS(app)

async def fetch_page(session, url, headers):
    try:
        async with session.get(url, headers=headers, timeout=15) as response:
            if response.status != 200:
                print(f"Failed to fetch page: {response.status}")
                return None
            return await response.text()
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None

async def scrape_jobs_async(company, role, location):
    keywords = f"{role} {company}"
    params = {
        'keywords': keywords,
        'location': location,
        'trk': 'public_jobs_jobs-search-bar_search-submit'
    }
    search_url = "https://www.linkedin.com/jobs/search/?" + urllib.parse.urlencode(params)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    async with aiohttp.ClientSession() as session:
        html_content = await fetch_page(session, search_url, headers)
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
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

async def scrape_all_jobs_async(companies, roles, locations):
    tasks = [
        scrape_jobs_async(company, role, location)
        for company, _ in companies
        for role, _ in roles
        for location, _ in locations
    ]
    all_jobs = await asyncio.gather(*tasks)
    return [job for job_list in all_jobs for job in job_list]

@app.route('/download_excel', methods=['GET'])
def download_excel():
    try:
        roles = json.loads(request.args.get("roles", "[]"))
        companies = json.loads(request.args.get("companies", "[]"))
        locations = json.loads(request.args.get("locations", "[]"))
        overall_weights = {
            "company_weight": float(request.args.get("overall_company_weight", 0)),
            "role_weight": float(request.args.get("overall_role_weight", 0)),
            "location_weight": float(request.args.get("overall_location_weight", 0))
        }

        # Validate weights
        if sum(overall_weights.values()) != 100:
            return jsonify({"error": "Overall weights must sum to 100%."}), 400

        async def main():
            jobs = await scrape_all_jobs_async(companies, roles, locations)
            unique_jobs = {frozenset(job.items()): job for job in jobs}.values()
            ranked_jobs = rank_jobs(list(unique_jobs), roles, companies, locations, overall_weights)

            df = pd.DataFrame(ranked_jobs)
            file_path = "job_data.xlsx"
            df.to_excel(file_path, index=False)
            return send_file(file_path, as_attachment=True, download_name="job_data.xlsx")

        return asyncio.run(main())
    except Exception as e:
        return jsonify({"error": f"Error generating Excel: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
