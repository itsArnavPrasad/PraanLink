#!/bin/bash

# Setup script for Google OAuth2 authentication
# This will authorize the application for Gmail and Calendar APIs

echo "=========================================="
echo "Google OAuth2 Setup for PraanLink"
echo "=========================================="
echo ""
echo "This script will:"
echo "1. Request authorization for Gmail and Calendar APIs"
echo "2. Save authentication tokens"
echo "3. Configure with your email addresses"
echo ""
echo "Email Configuration:"
echo "  Sender: anmolsureka006@gmail.com"
echo "  Receiver: arnav.prasad999918@gmail.com"
echo ""
read -p "Press Enter to continue..."

cd "$(dirname "$0")"

# Check if credentials.json exists
if [ ! -f "credentials.json" ]; then
    echo "❌ Error: credentials.json not found!"
    echo "Please make sure credentials.json is in the backend directory."
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Run the setup script
python utils/google_auth_setup.py

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Make sure your .env file has the email addresses configured"
echo "2. Test by running your backend server"
echo "3. Try the appointment booking feature"
echo ""