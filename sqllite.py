import sqlite3
import os

'''
jobs.db
table tree:
-jobs
--job ID (unique, from LN)
--title
--language
--description
--easy apply
--seniority_level

'''
db_name = 'jobs.db'
if os.path.isfile(db_name):
    db = sqlite3.connect(db_name)
    #cursor = db.cursor()
    rows = db.execute("SELECT * FROM jobs").fetchall()
    print(rows)

else: 
    db = sqlite3.connect(db_name)
    #cursor = db.cursor()
    db.execute('''
                   CREATE TABLE jobs (
                   jobID INTEGER PRIMARY KEY NOT NULL, 
                   title TEXT, 
                   language TEXT, 
                   description TEXT, 
                   easy_apply BOOLEAN DEFAULT 0, 
                   seniority TEXT)
                   ''')
    db.execute("INSERT INTO jobs VALUES (123, 'title', 'lng', 'desk', 1, 'intern')")
    db.commit()
    print('added')

db.close()