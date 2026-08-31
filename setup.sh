#!/bin/bash
# Smart Health Hub - Setup Script for Raspberry Pi OS

echo "=========================================="
echo "Smart Health Hub Setup"
echo "=========================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/device-tree/model 2>/dev/null; then
    echo "Warning: Not detected as Raspberry Pi. Some steps may not work correctly."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get current directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Project directory: $PROJECT_DIR"

# Update system
echo ""
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
sudo apt-get install -y python3-pip python3-dev libatlas-base-dev libjasper-dev
pip3 install --upgrade pip setuptools wheel

# Install Python packages
echo ""
echo "Installing Python packages from requirements.txt..."
cd "$PROJECT_DIR"
pip3 install -r requirements.txt

# Create directories
echo ""
echo "Creating application directories..."
mkdir -p data logs reports assets

# Set permissions
echo ""
echo "Setting file permissions..."
chmod +x "$PROJECT_DIR/main.py"

# Optional: Install SIM800L AT command utilities
echo ""
read -p "Install minicom for SIM800L testing? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo apt-get install -y minicom
fi

# Create desktop launcher
echo ""
read -p "Create desktop launcher? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    LAUNCHER_DIR="$HOME/.local/share/applications"
    mkdir -p "$LAUNCHER_DIR"
    
    LAUNCHER_FILE="$LAUNCHER_DIR/SmartHealthHub.desktop"
    cat > "$LAUNCHER_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Smart Health Hub
Comment=Smart Health Monitoring System
Exec=python3 $PROJECT_DIR/main.py
Icon=health
Terminal=false
Categories=Utility;Application;
StartupNotify=true
EOF
    
    echo "Desktop launcher created: $LAUNCHER_FILE"
fi

# Configure serial ports
echo ""
echo "Configuring serial port permissions..."
sudo usermod -a -G dialout $USER
echo "User added to dialout group (reboot needed for effect)"

# Test imports
echo ""
echo "Testing Python imports..."
python3 -c "
try:
    import PyQt5.QtWidgets
    print('✓ PyQt5 OK')
except ImportError as e:
    print(f'✗ PyQt5 failed: {e}')

try:
    import serial
    print('✓ PySerial OK')
except ImportError as e:
    print(f'✗ PySerial failed: {e}')

try:
    import reportlab
    print('✓ ReportLab OK')
except ImportError as e:
    print(f'✗ ReportLab failed: {e}')

try:
    import pyqtgraph
    print('✓ PyQtGraph OK')
except ImportError as e:
    print(f'⚠ PyQtGraph not installed (optional): {e}')
"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Reboot Raspberry Pi to apply serial port changes"
echo "2. Connect Arduino Mega 2560 via USB"
echo "3. Configure Arduino port in config.py if needed"
echo "4. Upload sketch to Arduino (arduino/sketch.ino)"
echo "5. Run: python3 $PROJECT_DIR/main.py"
echo ""
echo "Or use desktop launcher if created."
echo ""
