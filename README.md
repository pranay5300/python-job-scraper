# MBA/Masters Job Scraper - Daily Fresh Postings (2026 Start Dates)

🚀 **Automated job scraper that finds fresh MBA/Masters-level positions posted within the last 48 hours, with focus on 2026 start dates.**

## 🎯 Features

- **Daily Automated Scraping** - Runs daily at 8 AM to find fresh job postings
- **Multi-Source Scraping** - Indeed, LinkedIn, Glassdoor, and direct company career pages
- **Google Sheets Integration** - Outputs data directly to Google Sheets for Power BI connectivity
- **Email Notifications** - Daily email reports with job findings
- **Smart Filtering** - Focuses on MBA/Masters roles with 2026 start dates
- **Cloud Deployment** - Ready for deployment on Render.com or Docker

## 📊 Target Companies (200+ Companies)

The scraper targets major employers including:
- **Tech**: Amazon, Microsoft, Google, Meta, Apple, Tesla, etc.
- **Consulting**: McKinsey, BCG, Bain, Deloitte, PwC, etc.
- **Finance**: JPMorgan, Goldman Sachs, BlackRock, etc.
- **Energy**: ExxonMobil, Chevron, ConocoPhillips, etc.
- **CPG**: P&G, Unilever, PepsiCo, etc.
- **And many more...**

## 🔧 Setup Instructions

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd mba-job-scraper
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Google Sheets Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable **Google Sheets API** and **Google Drive API**
4. Create a **Service Account**
5. Download the JSON credentials file
6. Rename to `google_credentials.json` and place in project directory

Run the setup helper:
```bash
python google_sheets_setup.py
```

### 4. Email Configuration
Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

Edit `.env` with your details:
```env
# Email Configuration
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password  # Use Gmail App Password
RECIPIENT_EMAIL=recipient@gmail.com

# Google Sheets Configuration
GOOGLE_SHEET_SHARE_EMAIL=your-email@gmail.com
SPREADSHEET_NAME=MBA_Jobs_Daily_Feed
```

### 5. Test the Scraper
```bash
python test_scraper.py
```

## 🚀 Deployment on Render.com

### Method 1: Using render.yaml (Recommended)
1. Push code to GitHub
2. Connect GitHub repo to Render.com
3. Render will automatically detect `render.yaml`
4. Set environment variables in Render dashboard:
   - `SENDER_EMAIL`
   - `SENDER_PASSWORD`
   - `RECIPIENT_EMAIL`
   - `GOOGLE_CREDENTIALS_JSON` (entire JSON as string)
   - `GOOGLE_SHEET_SHARE_EMAIL`

### Method 2: Manual Setup
1. Create new **Worker** service on Render.com
2. Connect GitHub repository
3. Set build command:
   ```bash
   pip install -r requirements.txt
   ```
4. Set start command:
   ```bash
   python mba_job_scraper.py
   ```
5. Add environment variables (same as above)

## 🐳 Docker Deployment (Alternative)

```bash
# Build image
docker build -t mba-job-scraper .

# Run container
docker run -d \
  -e SENDER_EMAIL=your-email@gmail.com \
  -e SENDER_PASSWORD=your-password \
  -e RECIPIENT_EMAIL=recipient@gmail.com \
  -e GOOGLE_CREDENTIALS_JSON='{"type":"service_account",...}' \
  mba-job-scraper
```

## 📈 Power BI Integration

1. **Connect to Google Sheets**:
   - In Power BI, go to Get Data → Web
   - Use Google Sheets connector
   - Connect to your `MBA_Jobs_Daily_Feed` spreadsheet

2. **Set up Auto-Refresh**:
   - Configure Power BI to refresh data daily
   - The scraper updates the sheet every morning at 8 AM

3. **Create Dashboard**:
   - Visualize job trends by company, function, location
   - Track daily job posting volumes
   - Monitor visa sponsorship availability

## 📋 Data Schema

The scraper outputs data with these columns:
- **Company** - Company name
- **Role Title** - Job title
- **Function** - Job function (Product Management, Strategy, etc.)
- **Location** - Job location
- **Start Date** - Expected start date
- **Posted Date** - When job was posted
- **Visa Sponsorship** - Visa sponsorship status
- **Direct Link** - Link to apply
- **Key Qualifications** - Job requirements summary
- **Source** - Where job was found
- **Scraped At** - When data was collected

## ⚙️ Configuration Options

Edit `config.py` or use environment variables:

```python
# Scraping frequency
DAILY_RUN_TIME = "08:00"  # 8 AM daily

# Rate limiting
REQUEST_DELAY = 2.0  # Seconds between requests
MAX_JOBS_PER_COMPANY = 5  # Max jobs per company

# Run once for testing
RUN_ONCE = true
```

## 🔍 Search Criteria

The scraper looks for jobs with:
- **Employment Type**: Full-time only
- **Start Dates**: May 2026 or later
- **Functions**: Product Management, Strategy, Marketing, etc.
- **Education**: MBA/Masters required or preferred
- **Location**: US-based positions
- **Recency**: Posted within last 48 hours

**Excludes**:
- Internships, co-ops, fellowships
- Contract/temporary roles
- Academic positions
- Senior roles requiring 7+ years experience

## 🛠️ Troubleshooting

### Common Issues:

1. **No jobs found**:
   - This is normal - not all companies post daily
   - Check if websites have changed structure
   - Verify rate limiting isn't blocking requests

2. **Google Sheets error**:
   - Verify service account has correct permissions
   - Check if spreadsheet exists and is shared
   - Ensure APIs are enabled in Google Cloud

3. **Email not sending**:
   - Use Gmail App Password, not regular password
   - Check SMTP settings
   - Verify sender email is correct

4. **Selenium issues on Render**:
   - Chrome and ChromeDriver are installed via `render.yaml`
   - Use headless mode (already configured)

## 📊 Expected Results

- **Daily Volume**: 10-50 jobs per day (varies by market conditions)
- **Peak Times**: Monday-Wednesday typically have more postings
- **Seasonal Patterns**: Higher volume in fall recruiting season
- **Success Rate**: ~70-80% of target companies will be successfully scraped

## 🤝 Contributing

To add more companies or improve scraping:
1. Edit `target_companies` list in `mba_job_scraper.py`
2. Add new scraping methods for specific job boards
3. Improve job relevance filtering
4. Enhance data extraction accuracy

## 📝 License

MIT License - feel free to modify and use for your job search!

## 🆘 Support

For issues or questions:
1. Check the logs: `job_scraper.log`
2. Test with: `python test_scraper.py`
3. Verify configuration in `.env` file

---

**Happy job hunting! 🎯**

*This scraper helps you stay on top of the latest MBA/Masters opportunities from top companies, delivered fresh to your inbox every morning.*