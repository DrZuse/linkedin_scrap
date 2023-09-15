import sqlite3
import os

'''
jobs.db
table tree:
-jobs
--jobID (unique, from LN)
--title
--language
--description
--easy apply
--seniority_level

'''
db_name = 'jobs.db'

def job_ids(db):
    jids = db.execute("SELECT jobID FROM jobs").fetchall()
    result = [i[0] for i in jids]
    return result



# if os.path.isfile(db_name):
#     db = sqlite3.connect(db_name)
#     # #cursor = db.cursor()
#     # rows = db.execute("SELECT * FROM jobs").fetchall()
#     # print(rows)
#     job_ids(db)

# else: 
#     db = sqlite3.connect(db_name)
#     job_ids(db)
#     # db.execute('''
#     #                CREATE TABLE jobs (
#     #                jobID INTEGER PRIMARY KEY NOT NULL, 
#     #                title TEXT, 
#     #                language TEXT, 
#     #                description TEXT, 
#     #                easy_apply BOOLEAN DEFAULT 0, 
#     #                seniority TEXT)
#     #                ''')
#     # db.execute("INSERT INTO jobs VALUES (123, 'title', 'lng', 'desk', 1, 'intern')")
#     # db.execute("INSERT INTO jobs VALUES (124, 'title2', 'lng2', 'desk2', 0, 'eprrt')")
#     # db.commit()
#     print('added')
db = sqlite3.connect(db_name)
db.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
    jobID INTEGER PRIMARY KEY NOT NULL, 
    title TEXT, 
    language TEXT, 
    description TEXT, 
    easy_apply BOOLEAN DEFAULT 0, 
    seniority TEXT)
''')

print(job_ids(db))
db.close()