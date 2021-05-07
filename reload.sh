#!/usr/bin/bash
killall /usr/bin/python3
git pull
chmod +x ./main.py
./main.py
