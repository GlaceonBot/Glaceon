import os
import pathlib
import random
import string
from sys import platform

from dotenv import load_dotenv

path = pathlib.PurePath()
if "linux" not in platform:
    print("This script is for linux!")
    exit(0)

if os.geteuid() != 0:
    print("Whoa whoa whoa! This file needs to be run as root! (sudo)")
    exit(0)

try:
    pathlib.Path(path / "Glaceon").mkdir()
    path = pathlib.PurePath(path / "Glaceon")
except FileExistsError:
    print("Directory Glaceon exists already!")
    exit(0)

sql_password = ''.join(random.choice(string.printable) for i in range(0, 30))

os.system("apt install python3 python3-venv python3-pip mysql-server webhook -y")
token = input("Input bot token for .env: ")
path = pathlib.PurePath("Glaceon")
os.system(f"mysql -u root -h localhost -e \"CREATE USER 'glaceon'@'localhost' IDENTIFIED BY '{sql_password}'\"")
os.system(f"mysql -u root -h localhost -e \"GRANT ALL PRIVILEGES ON database_name.* TO 'username'@'localhost'\"")

os.system("git clone https://github.com/GlaceonBot/Glaceon")
os.system(f"python3 -m venv {path}/venv")
import mysql.connector

with open("env", 'w+') as dotenv:
    dotenv.write(f"""TOKEN=\"{token}\"
SQLusername=\"glaceon\"
SQLpassword=\"{sql_password}\"
SQLserverhost="localhost"
SQLdatabase=\"glaceondata\"""")
load_dotenv()
db = mysql.connector.connect(host=os.getenv('SQLserverhost'),
                             user=os.getenv('SQLusername'),
                             password=os.getenv('SQLpassword'),
                             db=os.getenv('SQLdatabase')).cursor()
db.execute('''CREATE TABLE IF NOT EXISTS settings (serverid BIGINT, setto BIGINT, setting TEXT)''')
db.execute('''CREATE TABLE IF NOT EXISTS whitelisted_invites (hostguild BIGINT, inviteguild BIGINT)''')
db.execute('''CREATE TABLE IF NOT EXISTS current_bans (serverid BIGINT,  userid BIGINT, banfinish BIGINT)''')
db.execute('''CREATE TABLE IF NOT EXISTS current_mutes (serverid BIGINT,  userid BIGINT, mutefinish BIGINT)''')
db.execute('''CREATE TABLE IF NOT EXISTS current_mutes (serverid BIGINT,  userid BIGINT, mutefinish BIGINT)''')
db.execute('''CREATE TABLE IF NOT EXISTS current_bans (serverid BIGINT,  userid BIGINT, banfinish BIGINT)''')
db.execute('''CREATE TABLE IF NOT EXISTS tags (serverid BIGINT, tagname TEXT, tagcontent TEXT)''')
db.execute('''CREATE TABLE IF NOT EXISTS prefixes (serverid BIGINT, prefix TEXT)''')
db.execute('''CREATE TABLE IF NOT EXISTS disabled_commands (serverid BIGINT, commandname TEXT, state BIT)''')
try:
    with open("/etc/systemd/system/glaceon.service", "w+") as servicefile:
        servicefile.write(f"""
    [Unit]
    Description=Glaceon discord bot
    After=network.target
    
    [Service]
    Type=simple
    User=root
    WorkDir={str(pathlib.PurePath) + "Glaceon"}
    ExecStart={str(pathlib.PurePath) + "Glaceon"}/start.sh
    
    [Install]
    WantedBy=multi-user.target""")
    os.system("systemctl start glaceon")
except Exception:
    print("Could not create service, you will have to manually add a service if you want one")
