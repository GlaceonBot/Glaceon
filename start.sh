#!/bin/bash
cd /home/Glaceon/Glaceon
./venv/bin/python3 -m pip install -r requirements.txt > glaceon.log 2>&1
./main.py > glaceon.log 2>&1
