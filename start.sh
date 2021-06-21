#!/bin/bash
cd /home/Glaceon/Glaceon
webhook -hooks glaceon-reloader-webhook.json -verbose > glaceon.log 2>&1 &
./main.py > glaceon.log 2>&1
