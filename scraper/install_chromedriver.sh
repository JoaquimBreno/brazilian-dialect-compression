#!/bin/bash

echo "Installing ChromeDriver for macOS..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found! Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install ChromeDriver
echo "Installing ChromeDriver via Homebrew..."
brew install --cask chromedriver

# Approve ChromeDriver in macOS security
echo "Approving ChromeDriver in macOS security..."
xattr -d com.apple.quarantine $(which chromedriver) 2>/dev/null || true

echo "ChromeDriver installation complete!"
echo "You can now run the scraper with: python suassuna_scraper.py" 