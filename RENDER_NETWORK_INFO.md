# 🌐 Render.com Network Configuration

## Static Outbound IP Addresses

When your JobDataCamp backend service makes outbound requests to external APIs or services, the requests will originate from one of these static IP addresses:

```
44.226.145.213
54.187.200.255
34.213.214.55
35.164.95.156
44.230.95.183
44.229.200.200
```

## 🔧 Use Cases for Static IPs

### 1. **API Whitelisting**
If your application needs to integrate with external APIs that require IP whitelisting:

```bash
# Example: Whitelist these IPs in your external API provider
# LinkedIn API, Indeed API, or other job board APIs
API_WHITELIST="44.226.145.213,54.187.200.255,34.213.214.55,35.164.95.156,44.230.95.183,44.229.200.200"
```

### 2. **Database Access Control**
For external database connections that require IP restrictions:

```sql
-- Example PostgreSQL IP restrictions
-- GRANT CONNECT ON DATABASE jobdatacamp TO jobdatacamp_user;
-- Add to pg_hba.conf:
host jobdatacamp jobdatacamp_user 44.226.145.213/32 md5
host jobdatacamp jobdatacamp_user 54.187.200.255/32 md5
host jobdatacamp jobdatacamp_user 34.213.214.55/32 md5
host jobdatacamp jobdatacamp_user 35.164.95.156/32 md5
host jobdatacamp jobdatacamp_user 44.230.95.183/32 md5
host jobdatacamp jobdatacamp_user 44.229.200.200/32 md5
```

### 3. **Firewall Configuration**
For corporate firewalls or security groups:

```bash
# AWS Security Group Rules
aws ec2 authorize-security-group-ingress \
    --group-id sg-xxxxxxxxx \
    --protocol tcp \
    --port 443 \
    --cidr 44.226.145.213/32

# Repeat for each IP...
```

## 🛡️ Security Considerations

### **Current JobDataCamp Security**
- ✅ **HTTPS Only**: All communications encrypted
- ✅ **CORS Configured**: Controlled frontend access
- ✅ **TAMU Authentication**: Email domain restriction (@tamu.edu)
- ✅ **No Database Exposure**: In-memory SQLite, no external connections
- ✅ **Static IPs**: Predictable outbound traffic

### **Future Integrations**
If you plan to add real job scraping from external APIs:

1. **LinkedIn Jobs API**
   - Whitelist Render IPs in LinkedIn Developer Portal
   - Configure OAuth with static redirect URLs

2. **Indeed API**
   - Add IPs to Indeed Publisher account
   - Set up rate limiting based on IP

3. **MyVisaJobs Integration**
   - Configure scraping with IP rotation awareness
   - Implement respectful rate limiting

## 📊 Current Backend Outbound Requests

Your JobDataCamp backend currently makes minimal outbound requests:

```python
# Current outbound traffic from backend:
# - None (uses in-memory database)
# - Health check responses (inbound only)
# - Static job data (no external APIs)
```

## 🔧 Implementation for External APIs

If you want to add real job scraping, here's how to use the static IPs:

### **Example: Indeed API Integration**
```python
import requests

class IndeedAPIClient:
    def __init__(self):
        self.base_url = "https://api.indeed.com/ads/apisearch"
        self.static_ips = [
            "44.226.145.213",
            "54.187.200.255", 
            "34.213.214.55",
            "35.164.95.156",
            "44.230.95.183",
            "44.229.200.200"
        ]
    
    def search_jobs(self, query, location):
        # Your current IP will be one of the static IPs above
        params = {
            'publisher': 'YOUR_PUBLISHER_ID',
            'q': query,
            'l': location,
            'format': 'json'
        }
        
        response = requests.get(self.base_url, params=params)
        return response.json()
```

### **Example: LinkedIn Jobs Integration**
```python
class LinkedInJobsClient:
    def __init__(self):
        # Configure OAuth with redirect URL that accepts Render IPs
        self.client_id = "YOUR_CLIENT_ID"
        self.redirect_uri = "https://python-job-scraper.onrender.com/linkedin/callback"
        
    def get_jobs(self, access_token):
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        # API calls will come from Render's static IPs
        return requests.get('https://api.linkedin.com/v2/jobs', headers=headers)
```

## 🎯 Recommendations

### **For Production Deployment:**

1. **Document IPs**: Keep this list updated in your documentation
2. **Monitor Changes**: Render may update IPs occasionally
3. **Implement Graceful Failures**: Handle IP changes gracefully
4. **Rate Limiting**: Respect external API limits across all IPs

### **For TAMU Integration:**

```yaml
# If TAMU IT needs to whitelist your backend:
Service: JobDataCamp Backend
URL: https://python-job-scraper.onrender.com
Outbound IPs:
  - 44.226.145.213
  - 54.187.200.255
  - 34.213.214.55
  - 35.164.95.156
  - 44.230.95.183
  - 44.229.200.200
Purpose: Student job search platform with H1B predictions
```

## 📋 Troubleshooting

### **IP-Related Issues:**
If external services block requests:

1. **Check Current IP**:
   ```python
   import requests
   response = requests.get('https://api.ipify.org')
   print(f"Current IP: {response.text}")
   ```

2. **Verify IP Range**:
   ```bash
   # Should be one of the Render static IPs
   curl https://api.ipify.org
   ```

3. **Contact API Provider**:
   - Provide Render's static IP list
   - Request whitelisting for all 6 IPs

## 🔄 Updates

**Last Updated**: August 26, 2024  
**Source**: Render.com Dashboard > Network Settings  
**Status**: ✅ Active and documented

---

**Note**: These IPs are for outbound requests FROM your Render service TO external services. Inbound requests to your service come through Render's edge network and don't use these IPs.