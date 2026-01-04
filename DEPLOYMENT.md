# GC Resume Filter - Ubuntu Apache Deployment Guide

## Overview
This application is configured to run on Ubuntu Apache server at path `/resumefilter/` alongside other applications.

**Server IP**: 192.168.1.62  
**Application URL**: http://192.168.1.62/resumefilter/  
**API URL**: http://192.168.1.62/resumefilter/api

## Architecture

- **Frontend**: React app served from `/var/www/html/resumefilter/frontend/`
- **Backend**: FastAPI running on port 8000 (localhost only)
- **Proxy**: Apache proxies `/resumefilter/api` to backend port 8000

## Files Overview

- `deploy.sh` - Main deployment script
- `apache-config.conf` - Apache configuration template (uses path-based routing)
- `pre-deploy-check.sh` - Pre-deployment validation script
- `.env` - Environment variables (contains OpenAI API key)

## Deployment Steps

### 1. Pre-Deployment Check (Optional but Recommended)

On the Ubuntu server, run:
```bash
bash pre-deploy-check.sh
```

This checks for:
- Apache installation and status
- Required Apache modules
- Python3, pip, Node.js, npm
- Port 8000 availability
- Directory permissions
- Existing deployments

### 2. Deploy

Run the deployment script:
```bash
sudo bash deploy.sh
```

The script will:
1. Confirm deployment location (`/var/www/html/resumefilter/`)
2. Install backend dependencies (creates Python venv)
3. Install frontend dependencies (npm)
4. Build frontend with base path `/resumefilter/`
5. Deploy frontend to `/var/www/html/resumefilter/`
6. Configure Apache (backs up existing config)
7. Enable required Apache modules
8. Test Apache configuration (rolls back on failure)
9. Setup systemd service for backend
10. Start backend service

### 3. Verify Deployment

After deployment, check:

```bash
# Check backend service status
sudo systemctl status gc-resumefilter-backend

# Check backend logs
sudo journalctl -u gc-resumefilter-backend -f

# Check Apache configuration
sudo apache2ctl configtest

# Access application
curl http://192.168.1.62/resumefilter/
```

## Important Notes

### Path-Based Routing
The application uses path-based routing (not VirtualHost) to coexist with other sites:
- Uses `Alias` directive for frontend
- Uses `Location` directive for API proxy
- Configuration stored in `/etc/apache2/conf-available/` (not sites-available)

### No Conflicts with Other Sites
The deployment:
- ✅ Does NOT modify existing VirtualHost configuration
- ✅ Does NOT disable other sites
- ✅ Does NOT interfere with `/erp/`, `/ocr/`, or other paths
- ✅ Uses separate log files
- ✅ Runs backend on dedicated port 8000

### Backend Location
- Backend runs from original project directory (not /var/www/html)
- Only frontend is copied to /var/www/html
- Backend managed by systemd service

### Environment Variables
The `.env` file contains:
```
OPENAI_API_KEY=your_key_here
USE_OPENAI=True
MIN_KEYWORD_SCORE=50
```

Ensure this file exists in project root before deployment.

## Management Commands

### Backend Service
```bash
# Start service
sudo systemctl start gc-resumefilter-backend

# Stop service
sudo systemctl stop gc-resumefilter-backend

# Restart service
sudo systemctl restart gc-resumefilter-backend

# View status
sudo systemctl status gc-resumefilter-backend

# View logs
sudo journalctl -u gc-resumefilter-backend -f

# Disable auto-start on boot
sudo systemctl disable gc-resumefilter-backend

# Enable auto-start on boot
sudo systemctl enable gc-resumefilter-backend

# Backup Job Profiles
```bash
# Add to crontab
sudo crontab -e
# Add this line to backup job profiles weekly at 3 AM every Sunday:
0 3 * * 0 cp -f /path/to/source/file.json /path/to/destination/
```

### Apache
```bash
# Test configuration
sudo apache2ctl configtest

# Restart Apache
sudo systemctl restart apache2

# Reload Apache (graceful)
sudo systemctl reload apache2

# View Apache logs
sudo tail -f /var/log/apache2/gc_resumefilter_error.log
sudo tail -f /var/log/apache2/gc_resumefilter_access.log

# Disable resume filter (without uninstalling)
sudo a2disconf gc-resumefilter.conf
sudo systemctl reload apache2

# Re-enable resume filter
sudo a2enconf gc-resumefilter.conf
sudo systemctl reload apache2
```

## Rollback

If deployment fails or you need to rollback:

### Remove Resume Filter
```bash
# Disable Apache configuration
sudo a2disconf gc-resumefilter.conf
sudo systemctl reload apache2

# Stop and disable backend service
sudo systemctl stop gc-resumefilter-backend
sudo systemctl disable gc-resumefilter-backend

# Remove frontend deployment (optional - keeps backups)
sudo rm -rf /var/www/html/resumefilter/frontend

# Restore previous configuration (if needed)
sudo cp /etc/apache2/conf-available/gc-resumefilter.conf.backup.* \
        /etc/apache2/conf-available/gc-resumefilter.conf
```

### Restore from Backup
Backups are created with timestamps:
- Apache config: `/etc/apache2/conf-available/gc-resumefilter.conf.backup.YYYYMMDD_HHMMSS`
- Frontend: `/var/www/html/resumefilter/frontend.backup.YYYYMMDD_HHMMSS`

## Troubleshooting

### Frontend not loading
1. Check Apache error log: `sudo tail -f /var/log/apache2/gc_resumefilter_error.log`
2. Verify files exist: `ls -la /var/www/html/resumefilter/frontend/`
3. Check permissions: `ls -la /var/www/html/resumefilter/`
4. Test Apache config: `sudo apache2ctl configtest`

### API not responding
1. Check backend service: `sudo systemctl status gc-resumefilter-backend`
2. Check backend logs: `sudo journalctl -u gc-resumefilter-backend -n 50`
3. Check port 8000: `sudo ss -tulnp | grep :8000`
4. Check Apache proxy: `curl -v http://localhost/resumefilter/api/health`

### Port 8000 already in use
```bash
# Find what's using port 8000
sudo ss -tulnp | grep :8000

# If it's an old instance of the backend
sudo systemctl stop gc-resumefilter-backend
sudo systemctl start gc-resumefilter-backend
```

### Apache configuration test fails
```bash
# View detailed error
sudo apache2ctl configtest

# Check for syntax errors in config
sudo cat /etc/apache2/conf-available/gc-resumefilter.conf

# Disable config and try again
sudo a2disconf gc-resumefilter.conf
sudo apache2ctl configtest
```

## Security Considerations

1. **API Key**: Keep `.env` file secure, not world-readable
   ```bash
   chmod 600 .env
   ```

2. **Backend Port**: Port 8000 only listens on localhost (127.0.0.1), not exposed externally

3. **File Permissions**: Frontend files owned by www-data:www-data with 755 permissions

4. **HTTPS**: For production, consider setting up SSL/TLS certificate

## Updating the Application

### Update Frontend Only
```bash
cd /path/to/project/frontend
npm run build
sudo cp -r dist/* /var/www/html/resumefilter/frontend/
```

### Update Backend Only
```bash
cd /path/to/project/backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart gc-resumefilter-backend
```

### Full Redeployment
```bash
sudo bash deploy.sh
```

## Contact

For issues or questions, refer to the project repository or contact the development team.
