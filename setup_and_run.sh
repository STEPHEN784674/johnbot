cat << 'EOF' > setup_and_run.sh
#!/bin/bash

echo "📦 Updating system..."
sudo apt update -y && sudo apt upgrade -y

echo "🐍 Installing Python and pip..."
sudo apt install -y python3 python3-pip screen

echo "📦 Installing required Python modules..."
pip3 install --upgrade pip
pip3 install python-telegram-bot nest_asyncio apscheduler

echo "📁 Creating bot folder..."
mkdir -p ~/telegrambot
cd ~/telegrambot

echo "📄 Writing bot script..."
cat << 'EOPY' > forwardbot.py
# === Your entire forwardbot.py script goes here ===
# Replace this placeholder with your actual working code
print("🚀 Replace this line with your real bot script.")
EOPY

echo "🚀 Launching bot in a screen session..."
screen -dmS telegrambot python3 ~/telegrambot/forwardbot.py

echo "✅ Bot is now running in background screen session called 'telegrambot'"
EOF
