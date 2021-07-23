#!/bin/bash
cd /home/Glaceon/Glaceon
./venv/bin/python -m pip install -r requirements.txt > glaceon.log 2>&1
./main.py --loglevel=info
