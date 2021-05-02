#!/usr/bin/bash
killall ./main.py
git pull
chmod +x ./main.py
./main.py
