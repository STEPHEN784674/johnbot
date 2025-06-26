#!/bin/bash

echo "🔄 Updating apt..."
sudo apt update

echo "📦 Installing python3-venv and curl..."
sudo apt install -y python3-venv curl

echo "📁 Creating project venv..."
python3 -m venv venv

echo "📂 Activating venv..."
source venv/bin/activate

echo "⬆️ Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing required Python packages..."
pip install python-telegram-bot apscheduler nest_asyncio

echo "🚀 Running your bot now..."
python3 forwardbot.py

echo "🚀 Running bot..."
python forwardbot.py
