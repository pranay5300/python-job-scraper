from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os
import json

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Mock function to simulate job scraping (replace this with real scraping or database queries)
def mock_scrape_jobs(company, role, location, job_type):
    return [
        {"Job Title": f"{role} Engineer", "Company Name": company, "Location": location, "Job Link": "http://example.com/job1"},
        {"Job Title": f"{role} Manager", "Company Name": company, "Location": location, "Job Link": "http://example.com/job2"},
        {"Job Title": "Software Developer", "Company Name": "Tech Corp", "Location": "Remote", "Job Link": "http://example.com/job3"},
    ]

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

        # Get job data (replace mock function with actual scraping or database query)
        jobs = mock_scrape_jobs("test company", "test role", "test location", "full-time")

        # Check if jobs were found
        if not jobs:
            return jsonify({"error": "No jobs found"}), 404

        # Rank jobs based on weights
        ranked_jobs = rank_jobs(jobs, weights, "test role", "test location", "test company")

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
