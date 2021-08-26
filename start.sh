#!/bin/bash
cd $HOME/Glaceon
./venv/bin/pip install -U -r requirements.txt > glaceon.log 2>&1
./main.py --loglevel=info
