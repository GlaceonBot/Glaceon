#!/bin/bash
git fetch
git reset --hard origin/master
sudo chmod +x start.sh
sudo chmod +x update.sh
sudo chmod +x main.py
sudo systemctl restart glaceon.service
