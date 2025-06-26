#!/bin/bash

# Move to script directory
cd "$(dirname "$0")"

echo "🔄 Updating package list..."
sudo apt update

echo "🐍 Installing Python 3.12 and venv..."
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-distutils curl

# Make python3.12 default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1
sudo update-alternatives --set python3 /usr/bin/python3.12

# Install pip for Python 3.12 if missing
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.12

echo "📦 Creating virtual environment..."
python3.12 -m venv venv || {
    echo "❌ Failed to create virtualenv.";
    exit 1;
}

echo "✅ Virtual environment created."

echo "📥 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install python-telegram-bot apscheduler nest_asyncio

echo "🚀 Running bot..."
python forwardbot.py
