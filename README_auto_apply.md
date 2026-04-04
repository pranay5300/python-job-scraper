# LinkedIn Auto-Apply for Supply Chain Rotational Programs

🤖 **Automated LinkedIn job application system specifically designed for supply chain rotational programs and entry-level positions across the USA.**

## 🎯 Features

### **Core Functionality**
- ✅ **Automated LinkedIn Applications** - Apply to jobs with Easy Apply feature
- ✅ **Supply Chain Focus** - Targets rotational programs, operations, logistics, procurement roles
- ✅ **Smart Job Matching** - AI-powered job relevance scoring
- ✅ **Resume Management** - Multiple specialized resume versions
- ✅ **Safety & Rate Limiting** - Human-like behavior to avoid detection
- ✅ **Comprehensive Tracking** - Google Sheets integration for analytics

### **Advanced Features**
- 🔗 **Simplify Integration** - Enhanced job matching using Simplify platform
- 📊 **Power BI Ready** - Direct Google Sheets output for dashboard creation  
- 📧 **Daily Email Reports** - Automated application summaries
- 🛡️ **Anti-Detection** - Stealth mode with human simulation
- 📈 **Performance Analytics** - Success rate tracking and optimization

## 🎯 Target Roles

The system specifically searches for:
- **Supply Chain Rotational Programs**
- **Operations Management Trainee**
- **Logistics Leadership Development**
- **Procurement Analyst (Entry Level)**
- **Supply Chain Analyst**
- **Inventory Management Associate**
- **Demand Planning Analyst**
- **Manufacturing Operations Trainee**

## 🏢 Target Companies (200+)

### **Technology**
Amazon, Microsoft, Google, Apple, Meta, Tesla, Intel, Dell Technologies, etc.

### **Retail & E-commerce**
Walmart, Target, Home Depot, Costco, Best Buy, Kroger, CVS Health, etc.

### **Manufacturing**
General Electric, 3M, Boeing, Caterpillar, Ford, GM, Honeywell, etc.

### **Consumer Goods**
P&G, Unilever, J&J, PepsiCo, Coca-Cola, Nestle, Mars, etc.

### **Logistics & Transportation**
FedEx, UPS, DHL, C.H. Robinson, XPO Logistics, etc.

*[Full list of 200+ companies included in system]*

## 🚀 Quick Start

### 1. **Installation**
```bash
git clone <repository-url>
cd linkedin-auto-apply
pip install -r requirements_auto_apply.txt
```

### 2. **Configuration**
```bash
# Create configuration from template
cp .env_auto_apply.example .env
cp auto_apply_config_template.json auto_apply_config.json

# Edit with your credentials
nano .env
nano auto_apply_config.json
```

### 3. **Setup Resume Versions**
```bash
# Create specialized supply chain resume versions
python main_auto_apply.py --setup-resumes path/to/your/resume.pdf
```

### 4. **Test System**
```bash
# Test all components
python main_auto_apply.py --mode test
```

### 5. **Run Single Session**
```bash
# Apply to 10 jobs
python main_auto_apply.py --mode single --max-applications 10
```

### 6. **Run Scheduled Sessions**
```bash
# Run automated daily sessions
python main_auto_apply.py --mode scheduled
```

## ⚙️ Configuration

### **LinkedIn Credentials**
```env
LINKEDIN_EMAIL=your-email@example.com
LINKEDIN_PASSWORD=your-password
LINKEDIN_PHONE=+1-555-123-4567
```

### **Safety Settings**
```env
MAX_APPLICATIONS_PER_DAY=25
MAX_APPLICATIONS_PER_HOUR=5
MAX_APPLICATIONS_PER_COMPANY=2
MIN_DELAY_BETWEEN_APPLICATIONS=45
MAX_DELAY_BETWEEN_APPLICATIONS=120
```

### **Simplify Integration (Optional)**
```env
SIMPLIFY_EMAIL=your-simplify-email@example.com
SIMPLIFY_PASSWORD=your-simplify-password
```

### **Google Sheets Setup**
1. Create Google Cloud Project
2. Enable Google Sheets API & Google Drive API
3. Create Service Account
4. Download JSON credentials
5. Set `GOOGLE_CREDENTIALS_JSON` environment variable

## 🛡️ Safety Features

### **Rate Limiting**
- Maximum 25 applications per day
- Maximum 5 applications per hour  
- Maximum 2 applications per company
- 45-120 second delays between applications
- Automatic cooldown periods

### **Anti-Detection**
- Human-like typing simulation
- Random mouse movements
- Natural scrolling behavior
- Stealth browser configuration
- User agent randomization
- CAPTCHA detection and handling

### **Activity Tracking**
- SQLite database for all activities
- Daily/weekly performance reports
- Success rate monitoring
- Error tracking and alerts

## 📊 Data Output

### **Google Sheets Schema**
| Column | Description |
|--------|-------------|
| Company | Company name |
| Job Title | Position title |
| Function | Job category (Operations, Logistics, etc.) |
| Location | Job location |
| Application Status | Applied/Failed/Pending |
| Applied Date | Timestamp |
| Visa Sponsorship | Sponsorship information |
| Direct Link | Job posting URL |
| Key Qualifications | Job requirements |
| Source | LinkedIn/Simplify |
| Simplify Score | AI match score |

### **Power BI Integration**
1. Connect Power BI to your Google Sheets
2. Set up auto-refresh (daily)
3. Create dashboards for:
   - Application success rates
   - Company application tracking
   - Job function analysis
   - Geographic distribution
   - Timeline trends

## 🎯 Resume Management

### **Specialized Versions**
The system automatically creates optimized resume versions:
- **Supply Chain Operations** - Manufacturing, process improvement focus
- **Logistics Coordination** - Transportation, distribution focus  
- **Procurement Specialist** - Sourcing, vendor management focus
- **Supply Planning** - Demand planning, forecasting focus
- **Rotational Programs** - Leadership development focus

### **Smart Selection**
- AI matches resume version to job requirements
- Tracks performance of each version
- Recommends optimizations based on success rates

## 📧 Email Reports

Daily automated reports include:
- **Applications Summary** - Success/failure counts
- **Company Breakdown** - Applications by company
- **Job Function Analysis** - Role categories applied to
- **Performance Metrics** - Success rates and trends
- **Recommendations** - System optimization suggestions

## 🔧 Advanced Usage

### **Command Line Options**
```bash
# Single session with custom limits
python main_auto_apply.py --mode single --max-applications 15

# Test specific components  
python main_auto_apply.py --mode test

# Setup with custom config
python main_auto_apply.py --config my_config.json --mode single

# Create resume versions
python main_auto_apply.py --setup-resumes resume.pdf
```

### **Scheduled Operations**
The system runs automatically:
- **9:00 AM** - Morning application session (10 applications)
- **2:00 PM** - Afternoon session (8 applications)  
- **7:00 PM** - Evening session (7 applications)
- **Sunday 2:00 AM** - Weekly maintenance and reports

### **Customization**
Edit configuration files to customize:
- Target companies list
- Job search keywords
- Application limits and timing
- Email templates
- Resume selection logic

## 📈 Performance Optimization

### **Success Rate Improvement**
- Monitor application-to-response ratios
- A/B test different resume versions
- Optimize job targeting based on success rates
- Adjust application timing for better results

### **Quality Over Quantity**
- Focus on high-match jobs (70%+ compatibility)
- Prioritize rotational programs and target companies
- Maintain human-like application patterns
- Regular system health monitoring

## ⚠️ Important Considerations

### **LinkedIn Terms of Service**
- This tool automates LinkedIn interactions
- Use responsibly and within reasonable limits
- Monitor your account for any restrictions
- Consider LinkedIn Premium for better visibility

### **Legal Compliance**
- Ensure resume information is accurate
- Respect company application processes
- Follow up appropriately on applications
- Maintain professional communication

### **Best Practices**
- Start with low application limits (5-10/day)
- Monitor success rates and adjust strategy
- Keep resume and profile updated
- Personalize follow-up communications
- Track and respond to employer outreach

## 🛠️ Troubleshooting

### **Common Issues**

1. **Login Failures**
   - Verify LinkedIn credentials
   - Check for 2FA requirements
   - Clear browser cache/cookies
   - Try manual login first

2. **No Jobs Found**
   - Adjust search keywords
   - Expand location criteria  
   - Check date filters
   - Verify company list accuracy

3. **Application Failures**
   - Check Easy Apply availability
   - Verify resume upload functionality
   - Review required fields completion
   - Monitor rate limiting

4. **Google Sheets Errors**
   - Verify service account permissions
   - Check API quotas and limits
   - Ensure spreadsheet exists and is shared
   - Test credentials manually

### **Logs and Debugging**
- Check `linkedin_auto_apply.log` for detailed logs
- Use `--mode test` to verify component health
- Monitor safety database for activity patterns
- Review email reports for system status

## 📊 Expected Results

### **Typical Performance**
- **Application Success Rate**: 85-95% (Easy Apply jobs)
- **Response Rate**: 2-5% (industry average)
- **Interview Rate**: 0.5-2% (varies by market conditions)
- **Daily Applications**: 15-25 (within safety limits)

### **Timeline Expectations**
- **Week 1-2**: System setup and optimization
- **Week 3-4**: Initial responses and interviews
- **Month 2-3**: Offer negotiations and decisions
- **Seasonal Variations**: Higher activity in fall recruiting

## 🤝 Contributing

To improve the system:
1. Fork the repository
2. Add new company targets
3. Enhance job matching algorithms
4. Improve safety mechanisms
5. Submit pull requests

## 📝 License

MIT License - Use responsibly for your job search

---

## 🆘 Support

For issues or questions:
1. Check logs and error messages
2. Review configuration settings
3. Test individual components
4. Consult troubleshooting guide

**Happy job hunting! 🎯**

*This system helps you efficiently apply to supply chain rotational programs while maintaining professional standards and LinkedIn compliance.*