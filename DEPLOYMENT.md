# Deployment Guide - Smart Health Hub

This guide explains how to deploy the Smart Health Hub application from development to Raspberry Pi production deployment.

## Pre-Deployment Checklist

- [ ] Arduino Mega code uploaded and tested
- [ ] All hardware components connected and verified
- [ ] Raspberry Pi OS installed and updated
- [ ] Internet connection available on Raspberry Pi
- [ ] USB cables (Arduino and SIM800L) ready
- [ ] SIM card inserted in SIM800L (if SMS enabled)

## Step-by-Step Deployment

### 1. Transfer Files to Raspberry Pi

**Option A: Using SCP (from computer)**
```bash
scp -r SmartHealthHub/ pi@raspberrypi.local:/home/pi/
```

**Option B: Using GitHub**
```bash
cd /home/pi
git clone <repository-url> SmartHealthHub
cd SmartHealthHub
```

**Option C: USB Drive**
1. Copy SmartHealthHub folder to USB drive on computer
2. Insert USB into Raspberry Pi
3. Copy to `/home/pi/SmartHealthHub`

### 2. Run Setup Script

```bash
cd /home/pi/SmartHealthHub
bash setup.sh
```

This will:
- Update system packages
- Install Python dependencies
- Create necessary directories
- Configure serial ports
- Create desktop launcher (optional)

### 3. Hardware Verification

```bash
# Check USB devices
lsusb

# You should see:
# Arduino Mega 2560
# SIM800L (if connected)

# Verify ports
ls /dev/ttyUSB*

# Should show /dev/ttyUSB0 and/or /dev/ttyUSB1
```

### 4. Configure Application

Edit `/home/pi/SmartHealthHub/config.py`:

```python
# Set correct serial ports
ARDUINO_PORT = "/dev/ttyUSB0"      # Adjust if different
SIM800L_PORT = "/dev/ttyUSB1"      # Adjust if different

# Temperature sensor calibration
TEMPERATURE_OFFSET = 0
TEMPERATURE_MULTIPLIER = 1.0

# Feature flags
ENABLE_ECG = True
ENABLE_SMS = True
ENABLE_PDF = True
OFFLINE_MODE = False
```

### 5. Test Application

```bash
# First test - offline mode (no hardware needed)
python3 -c "
import sys
sys.path.insert(0, '/home/pi/SmartHealthHub')
from config import *
from ui.home import HomeScreen
print('✓ Imports successful')
"

# Run application with hardware
cd /home/pi/SmartHealthHub
python3 main.py
```

### 6. Verify Components

**Test Arduino:**
```bash
minicom -b 9600 -o -D /dev/ttyUSB0
# Type: AT (if ATmega firmware)
# Or just start the app and check logs
```

**Test SIM800L:**
```bash
minicom -b 9600 -o -D /dev/ttyUSB1
AT
# Should respond: OK
```

### 7. Create Auto-Start (Optional)

Create systemd service for auto-start on boot:

```bash
sudo nano /etc/systemd/system/smarthub.service
```

Add:
```ini
[Unit]
Description=Smart Health Hub
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/SmartHealthHub
ExecStart=/usr/bin/python3 /home/pi/SmartHealthHub/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable smarthub.service
sudo systemctl start smarthub.service
sudo systemctl status smarthub.service
```

### 8. Monitor Application

**View logs:**
```bash
tail -f /home/pi/SmartHealthHub/logs/app.log
```

**Check database:**
```bash
sqlite3 /home/pi/SmartHealthHub/data/app.db
```

**View generated reports:**
```bash
ls -lh /home/pi/SmartHealthHub/reports/
```

## Troubleshooting Deployment

### Issue: Import Errors

**Solution:**
```bash
# Verify Python version
python3 --version  # Should be 3.8+

# Reinstall dependencies
pip3 install --upgrade -r requirements.txt

# Check specific module
python3 -c "import PyQt5; print(PyQt5.__version__)"
```

### Issue: Display Not Working

**Check HDMI:**
```bash
tvservice -s  # Should show connected
```

**Check X Server:**
```bash
echo $DISPLAY  # Should show :0 or :1
DISPLAY=:0 xclock  # Test if X is running
```

### Issue: Touchscreen Not Calibrated

```bash
# Calibrate touchscreen
DISPLAY=:0 xinput_calibrator

# Or use Raspberry Pi Settings GUI
```

### Issue: Serial Ports Not Accessible

```bash
# Check permissions
ls -l /dev/ttyUSB*

# Fix if needed
sudo chmod 666 /dev/ttyUSB0
sudo chmod 666 /dev/ttyUSB1

# Or add user to group (permanent)
sudo usermod -a -G dialout $USER
# Reboot for effect
```

## Performance Optimization

### Memory
- Raspberry Pi 4: Recommended 4GB+ RAM
- Monitor with: `free -h`

### Storage
- Requires ~500MB for installation
- Database grows ~1KB per test
- PDFs require ~50-200KB each
- Monitor with: `df -h`

### Display
- Ensure proper refresh rate
- Check GPU memory allocation
- Monitor temperature: `vcgencmd measure_temp`

## Backup & Recovery

### Backup Patient Data

```bash
# Backup database
cp /home/pi/SmartHealthHub/data/app.db \
   /home/pi/SmartHealthHub/data/app.db.backup.$(date +%Y%m%d)

# Backup all data
tar -czf SmartHealthHub_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
         /home/pi/SmartHealthHub/data \
         /home/pi/SmartHealthHub/reports
```

### Restore Data

```bash
# Restore from backup
cp /home/pi/SmartHealthHub/data/app.db.backup.20260831 \
   /home/pi/SmartHealthHub/data/app.db
```

## Updates & Maintenance

### Update Application Code

```bash
cd /home/pi/SmartHealthHub
git pull origin main  # If using GitHub

# Or manually replace files
# Then restart application
```

### Update Dependencies

```bash
pip3 install --upgrade -r requirements.txt
```

### Clean Up Old Files

```bash
# Remove old reports (keep last 100)
cd /home/pi/SmartHealthHub/reports
ls -t | tail -n +101 | xargs rm -f

# Remove old logs (keep last 10MB)
cd /home/pi/SmartHealthHub/logs
tail -c 10485760 app.log > app.log.tmp
mv app.log.tmp app.log
```

## Security Considerations

### 1. File Permissions

```bash
chmod 600 /home/pi/SmartHealthHub/config.py  # Sensitive config
chmod 600 /home/pi/SmartHealthHub/data/app.db  # Patient data
```

### 2. Network Security (if adding cloud)

- Use HTTPS for any remote connections
- Encrypt sensitive data in transit
- Validate all incoming data

### 3. Physical Security

- Touchscreen should be in secure location
- Limit USB access
- Secure Raspberry Pi enclosure

### 4. Data Privacy

- GDPR compliance for patient data storage
- Regular backups of patient database
- Secure deletion of old records if needed

## Monitoring

### Create Monitoring Script

```bash
#!/bin/bash
# monitor.sh - Monitor Smart Health Hub

while true; do
    echo "=== $(date) ==="
    
    # Check if app is running
    if pgrep -f "python3.*main.py" > /dev/null; then
        echo "✓ Application running"
    else
        echo "✗ Application NOT running"
    fi
    
    # Check disk space
    DISK=$(df /home/pi/SmartHealthHub | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    echo "Disk usage: $DISK%"
    
    if [ $DISK -gt 90 ]; then
        echo "⚠ WARNING: Disk usage high!"
    fi
    
    # Check database size
    DB_SIZE=$(ls -lh /home/pi/SmartHealthHub/data/app.db | awk '{print $5}')
    echo "Database size: $DB_SIZE"
    
    sleep 300  # Check every 5 minutes
done
```

Run:
```bash
chmod +x monitor.sh
./monitor.sh
```

## Support & Issues

### Getting Help

1. **Check Logs:**
   ```bash
   tail -100 /home/pi/SmartHealthHub/logs/app.log | grep ERROR
   ```

2. **Review Configuration:**
   ```bash
   cat /home/pi/SmartHealthHub/config.py | grep -v "^#"
   ```

3. **Test Hardware:**
   ```bash
   # Test Arduino
   minicom -b 9600 -o -D /dev/ttyUSB0
   
   # Test SIM800L
   minicom -b 9600 -o -D /dev/ttyUSB1
   ```

4. **Check System Health:**
   ```bash
   # CPU temperature
   vcgencmd measure_temp
   
   # Memory usage
   free -h
   
   # Disk space
   df -h /home/pi/SmartHealthHub
   ```

## Post-Deployment

### 1. User Training
- Demonstrate patient entry workflow
- Show test procedure
- Explain ECG electrode placement
- Review report generation

### 2. Documentation
- Keep copy of configuration
- Document hardware setup
- Create local troubleshooting guide
- Record serial port mappings

### 3. Testing
- Perform full test cycle monthly
- Verify database backups
- Check PDF generation
- Test SMS delivery

### 4. Maintenance Schedule

**Daily:**
- Monitor application logs
- Check for sensor errors

**Weekly:**
- Backup database
- Verify SMS delivery status
- Check disk space

**Monthly:**
- Full system test
- Review error logs
- Test emergency procedures

**Quarterly:**
- Recalibrate sensors
- Update software if available
- Test recovery procedures
- Review patient data

---

## Quick Reference

**Start Application:**
```bash
cd /home/pi/SmartHealthHub && python3 main.py
```

**View Logs:**
```bash
tail -f /home/pi/SmartHealthHub/logs/app.log
```

**Stop Application:**
```bash
pkill -f "python3.*main.py"
```

**Check Database:**
```bash
sqlite3 /home/pi/SmartHealthHub/data/app.db "SELECT COUNT(*) FROM patients;"
```

**Test Serial:**
```bash
minicom -b 9600 -o -D /dev/ttyUSB0
```

For more information, see README.md and QUICKSTART.md
