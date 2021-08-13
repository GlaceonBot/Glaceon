#!/bin/bash
cd $HOME/Glaceon
./venv/bin/python -m pip install -U -r requirements.txt > glaceon.log 2>&1
./main.py --loglevel=info
