import sqlite3


'''
jobs.db
table tree:
-jobs
--job ID (unique, from LN)
--title
--language
--description
--easy apply
--nseniority_level

'''

connection = sqlite3.connect("a2quarium.db")
print(connection.total_changes)