from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import os

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
        company = request.args.get("company", "").strip()
        role = request.args.get("role", "").strip()
        location = request.args.get("location", "").strip()
        job_type = request.args.get("jobType", "").strip()
        role_weight = float(request.args.get("role_weight", 0))
        location_weight = float(request.args.get("location_weight", 0))
        company_weight = float(request.args.get("company_weight", 0))

        # Validate weights
        if role_weight + location_weight + company_weight != 100:
            return jsonify({"error": "Weights must sum up to 100%"}), 400

        # Normalize weights
        weights = {
            "role_weight": role_weight / 100,
            "location_weight": location_weight / 100,
            "company_weight": company_weight / 100
        }

        # Get job data (replace mock function with actual scraping or database query)
        jobs = mock_scrape_jobs(company, role, location, job_type)

        # Check if jobs were found
        if not jobs:
            return jsonify({"error": "No jobs found"}), 404

        # Rank jobs based on weights
        ranked_jobs = rank_jobs(jobs, weights, role, location, company)

        # Save job data to Excel
        file_path = "job_data.xlsx"
        df = pd.DataFrame(ranked_jobs)
        df.to_excel(file_path, index=False)

        # Return the Excel file
        return send_file(file_path, as_attachment=True, download_name="job_data.xlsx")
    except Exception as e:
        return jsonify({"error": f"Error generating Excel: {e}"}), 500
    finally:
        # Cleanup the generated file
        if os.path.exists("job_data.xlsx"):
            os.remove("job_data.xlsx")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

