import os
import sqlite3

target_dir = os.path.expanduser('~/Applications/AppData/Local/Tolio/db')
if not os.path.exists(target_dir):
    os.makedirs(target_dir)
    connection = sqlite3.connect(os.path.expanduser(target_dir + "/portfolio.db"))
    
