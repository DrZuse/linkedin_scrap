import requests, time, os
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

all_proxies = [
    {'https': f"http://{i['username']}:{i['password']}@{i['internal_ip']}:{i['port_http']}"} 
    for i in dict_data
]

langs = ['en', 'uk', 'ru']

search_query = ' NOT '.join([
    '"python"', '"Canonical"', '"Sophilabs"', '"Turing"', '"TalentKompass"', '"Oowlish"', '"Listopro"', '"C++"', '"java"',
    '"C#"', '"Senior"', '"lead"', '"Développeur"', '"Programador"',
    '"Programmatore"', '"Analista"', '"Entwickler"', '"Entwicklun"', '"ingénieur"', '"codifica"',
    '"Werkstudent"', '"Programmieren"', '"Entwickler"', '"onsite"', '"on-site"', '"Principal"',
    '"Desarrollador"', '"Octopus IT"', '"remoto"', '"Teletrabajo"', '"tutor"', '"Sr."', '"SecOps"'
])

search_query = urllib.parse.quote(search_query)

def url(host_path, start_num=0, expirience=1):
    return ''.join([
        host_path, # 'https://www.linkedin.com/jobs/search?keywords='
        search_query,
        '&location=Worldwide',
        '&locationId=',
        '&geoId=92000000',
        '&f_TPR=r2592000',# time posted. r2592000 - past month
        '&f_WT=2', #  2 - remote
        '&f_E=', # expirience. 1 - intern, 2 - entry level
        str(expirience),
        '&position=1',
        '&pageNum=0',
        '&start=',
        str(start_num)
    ])

db_name = 'jobs.db'
db = sqlite3.connect(db_name)

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

def get_job_description(jid):
    time.sleep(random.uniform(0, 2))

    try:
        url = f'https://www.linkedin.com/jobs/view/{jid}'
        response = requests.get(url, proxies=random.choice(all_proxies))
        soup = BeautifulSoup(response.text, 'html.parser')
        
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
        

def main(expirience):
    try:
        # Send an HTTP GET request with the proxy settings
        host_path = 'https://www.linkedin.com/jobs/search?keywords='
        response = requests.get(url(host_path, 0, expirience), proxies=random.choice(all_proxies))
        print(url(host_path, 0, expirience))

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            print(soup.title.text)

            total_jobs = soup.find(attrs={'class': 'results-context-header__job-count'}).text.strip()
            print(total_jobs)

        else:
            print(f"Failed to retrieve the URL. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        raise Exception("fix error please")

    total_jobs = int(''.join(filter(str.isdigit, total_jobs)))

    pages = min(total_jobs//25, 40)
    print(f'pages: {pages}')


    start = 0
    for j in range(pages): # LinkedIn blocks requests when start > 1000
        print(f'page: {j} of {pages} | start: {start}')
        host_path = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords='

        try:
            # Send an HTTP GET request with the proxy settings
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

                jids = db.execute("SELECT jobID FROM jobs").fetchall()
                job_ids_from_db = [i[0] for i in jids]

                unique_job_ids = list(set(job_ids).difference(job_ids_from_db))
                print(f'unique_job_ids: {len(unique_job_ids)} || job_ids: {len(job_ids)}')
                with Pool(cpu_count()) as p:
                    jobs_info_list = p.map(get_job_description, unique_job_ids)

                jobs_info_list = [i for i in jobs_info_list if i is not None] # delete NoneType
                c = db.cursor()
                c.executemany('INSERT INTO jobs VALUES(?,?,?,?,?,?)', jobs_info_list)

                print('We have inserted', c.rowcount, 'records to the table.')

                #commit the changes to db			
                db.commit()
            else:
                print(f"Failed to retrieve the URL. Status code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

        start += 25

expirience_levels = [1,2,3,4]
for i in expirience_levels:
    main(i)

jids = db.execute("SELECT jobID FROM jobs").fetchall()
job_ids_from_db = [i[0] for i in jids]
print(f'total ids in DB: {len(job_ids_from_db)}')

db.close()