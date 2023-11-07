# Import necessary libraries
import requests, time
from bs4 import BeautifulSoup
import pandas as pd
import urllib
import sqlite3
from multiprocessing import Pool, cpu_count
import random
from langdetect import detect

# Specify the path to your CSV file with proxies
data = pd.read_csv('proxies.csv', sep=';') # CSV format: id;ip;port_http;port_socks5;username;password;internal_ip
dict_data = data.to_dict('records')

# Create a list of proxy dictionaries for use in requests
all_proxies = [
    {'https': f"http://{i['username']}:{i['password']}@{i['internal_ip']}:{i['port_http']}"} 
    for i in dict_data
]

# Define a list of languages to filter job descriptions
langs = ['en', 'uk', 'ru']

# Define a search query string by joining multiple keywords
search_query = ' NOT '.join([
    '"python"', '"Canonical"', '"Sophilabs"', '"Turing"', '"TalentKompass"', '"Oowlish"', '"Listopro"', '"C++"', '"java"',
    '"C#"', '"Senior"', '"lead"', '"Développeur"', '"Programador"',
    '"Programmatore"', '"Analista"', '"Entwickler"', '"Entwicklun"', '"ingénieur"', '"codifica"',
    '"Werkstudent"', '"Programmieren"', '"Entwickler"', '"onsite"', '"on-site"', '"Principal"',
    '"Desarrollador"', '"Octopus IT"', '"remoto"', '"Teletrabajo"', '"tutor"', '"Sr."', '"SecOps"'
])

# Encode the search query for use in URLs
search_query = urllib.parse.quote(search_query)

# Define a function to construct the URL for job searches
def url(host_path, start_num=0, expirience=1):
    return ''.join([
        host_path, # 'https://www.linkedin.com/jobs/search?keywords='
        search_query,
        '&location=Worldwide',
        '&locationId=',
        '&geoId=92000000',
        '&f_TPR=r2592000',# time posted. r2592000 - past month
        '&f_WT=2', #  2 - remote
        '&f_E=', # experience. 1 - intern, 2 - entry level
        str(expirience),
        '&position=1',
        '&pageNum=0',
        '&start=',
        str(start_num)
    ])

# Specify the name of the SQLite database and establish a connection
db_name = 'jobs.db'
db = sqlite3.connect(db_name)

# Create a table if it doesn't exist for storing job information
db.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        jobID           INTEGER PRIMARY KEY NOT NULL, 
        title           TEXT, 
        language        TEXT, 
        description     TEXT, 
        easy_apply      BOOLEAN DEFAULT 0,
        seniority       TEXT
    )
''')

# Define a function to retrieve the job description for a given job ID
def get_job_description(jid):
    time.sleep(random.uniform(0, 2))

    try:
        url = f'https://www.linkedin.com/jobs/view/{jid}'
        response = requests.get(url, proxies=random.choice(all_proxies))
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract job description, language, and other details
        description = soup.find(attrs={'class':'show-more-less-html__markup'}).text.strip()
        desc_lang = detect(description)
        easy_apply = soup.find(attrs={'class':'apply-button--default'}) is not None
        seniority_level = soup.find(attrs={'class':'description__job-criteria-text'}).text.strip()
        print(f'\ntitle: {soup.title.text}\ndescr: {description[:20]}...\nid: {jid}\nlang: {desc_lang}\neasy apply: {easy_apply}\nseniority_level: {seniority_level}')

        if desc_lang in langs:
            return (jid, soup.title.text, desc_lang, description, easy_apply, seniority_level)
        else:
            pass
    except Exception as e:
        print(f'{jid} - {e}')

# Define the main function to perform job searches for different experience levels
def main(expirience):
    try:
        # Send an HTTP GET request to the job search URL
        host_path = 'https://www.linkedin.com/jobs/search?keywords='
        response = requests.get(url(host_path, 0, expirience), proxies=random.choice(all_proxies))
        print(url(host_path, 0, expirience))

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            print(soup.title.text)

            # Extract the total number of jobs matching the search criteria
            total_jobs = soup.find(attrs={'class': 'results-context-header__job-count'}).text.strip()
            print(total_jobs)

        else:
            print(f"Failed to retrieve the URL. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        raise Exception("fix error please")

    total_jobs = int(''.join(filter(str.isdigit, total_jobs)))

    # Calculate the number of pages to scrape
    pages = min(total_jobs//25, 40)
    print(f'pages: {pages}')

    start = 0
    for j in range(pages): # LinkedIn blocks requests when start > 1000
        print(f'page: {j} of {pages} | start: {start}')
        host_path = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords='

        try:
            # Send an HTTP GET request to the job search URL for each page
            response = requests.get(url(host_path, start, expirience), proxies=random.choice(all_proxies))
            print(url(host_path, start, expirience))

            # Check if the request was successful (HTTP status code 200)
            if response.status_code == 200:
                # Parse the HTML content using BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                jobs_on_page = soup.find_all('li')

                # TODO: make language check
                job_ids = [
                    int(j.find(attrs={'class': 'base-card'})['data-entity-urn'].split(':')[-1])
                    for j in jobs_on_page 
                    if j.find(attrs={'class':'sr-only'}) is not None and detect(j.find(attrs={'class':'sr-only'}).text) in langs
                ]
                print(job_ids)
                print(len(job_ids))

                # Retrieve job IDs already present in the database
                jids = db.execute("SELECT jobID FROM jobs").fetchall()
               

                job_ids_from_db = [i[0] for i in jids]

                # Find unique job IDs not in the database
                unique_job_ids = list(set(job_ids).difference(job_ids_from_db))
                print(f'unique_job_ids: {len(unique_job_ids)} || job_ids: {len(job_ids)}')
                with Pool(cpu_count()) as p:
                    jobs_info_list = p.map(get_job_description, unique_job_ids)

                # Filter out NoneType job descriptions and insert into the database
                jobs_info_list = [i for i in jobs_info_list if i is not None]
                c = db.cursor()
                c.executemany('INSERT INTO jobs VALUES(?,?,?,?,?,?)', jobs_info_list)

                print('We have inserted', c.rowcount, 'records to the table.')

                # Commit the changes to the database
                db.commit()
            else:
                print(f"Failed to retrieve the URL. Status code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

        start += 25

# Define a list of experience levels for job searches
expirience_levels = [1,2,3,4]

# Perform job searches for different experience levels
for i in expirience_levels:
    main(i)

# Retrieve the job IDs from the database
jids = db.execute("SELECT jobID FROM jobs").fetchall()
job_ids_from_db = [i[0] for i in jids]
print(f'total IDs in DB: {len(job_ids_from_db)}')

# Close the database connection
db.close()