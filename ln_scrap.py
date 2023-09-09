import requests, time
from bs4 import BeautifulSoup
import pandas as pd
import urllib
from multiprocessing import Pool, cpu_count
import random
from langdetect import detect

# Specify the path to your CSV file
csv_file_path = "proxies.csv" # id;ip;port_http;port_socks5;username;password;internal_ip
data = pd.read_csv('proxies.csv', sep=';')
dict_data = data.to_dict('records')

proxy_server = dict_data[0]['internal_ip']
proxy_port_http = dict_data[0]['port_http']
proxy_port_socks5 = dict_data[0]['port_socks5']
proxy_username = dict_data[0]['username']
proxy_password = dict_data[0]['password']

langs = ['en', 'uk', 'ru']

proxies = {
    "https": f'http://{proxy_username}:{proxy_password}@{proxy_server}:{proxy_port_http}' 
}

search_query = ' NOT '.join([
    '"python"', '"Canonical"', '"Turing"', '"Oowlish"', '"Listopro"', '"C++"', '"java"',
    '"C#"', '"Softwareentwickler"', '"Senior"', '"tech lead"', '"Développeur"', '"Programador"',
    '"Programmatore"', '"Analista"', '"Entwickler"', '"Entwicklun"', '"ingénieur"', '"codifica"',
    '"Werkstudent"', '"Programmieren"', '"Remote after intial period"', '"Entwickler"',
    '"Desarrollador"', '"Octopus IT"', '"remoto"', '"Teletrabajo"', '"tutor"', '"Desenvolvedor"'
])

search_query = urllib.parse.quote(search_query)

url = f'https://www.linkedin.com/jobs/search?keywords={search_query}&location=Worldwide&locationId=&geoId=92000000&f_TPR=&f_WT=2&position=1&pageNum=0'


try:
    # Send an HTTP GET request with the proxy settings
    response = requests.get(url, proxies=proxies)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup.title.text)

        total_jobs = soup.find(attrs={'class': 'results-context-header__job-count'}).text.strip()
        #jobs_on_page = soup.find_all('li')
        print(total_jobs)

    else:
        print(f"Failed to retrieve the URL. Status code: {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    raise Exception("fix error please")



def get_job_description(jid):
    time.sleep(random.uniform(2, 4))

    try:
        url = 'https://www.linkedin.com/jobs/view/' + jid
        response = requests.get(url, proxies=proxies)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        description = soup.find(attrs={'class':'show-more-less-html__markup'}).text.strip()
        #desc_lang_en = detect(description) == 'en'
        desc_lang = detect(description)
        #if desc_lang_en == False:

        print(f'title: {soup.title.text}\ndescr: {description[:20]}...\nid: {jid}\nlang: {desc_lang}')
        #print(description[:20] + '...')
        #job_id = short_info.find(attrs)
    except Exception as e:
        print(jid + ' - ' + str(e))
        
    pass

total_jobs = int(''.join(filter(str.isdigit, total_jobs)))

pages = total_jobs//25
print(f'pages: {pages}')


start = 0
#for j in range(pages):
for j in range(3):
    print(f'page: {j} | start: {start}')
    url = ''.join([
        'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=',
        search_query,
        '&location=Worldwide&locationId=&geoId=92000000&f_TPR=&f_WT=2&position=1&pageNum=0&start=',
        str(start)
    ])

    # https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=
    #&location=Worldwide&locationId=&geoId=92000000&f_TPR=&f_WT=2&position=1&pageNum=0&start=0

    try:
        # Send an HTTP GET request with the proxy settings
        response = requests.get(url, proxies=proxies)

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            jobs_on_page = soup.find_all('li')

            # TODO: make language check
            job_ids = [
                j.find(attrs={'class': 'base-card'})['data-entity-urn'].split(':')[-1] 
                for j in jobs_on_page 
                if detect(j.find(attrs={'class':'sr-only'}).text) in langs
            ]
            print(job_ids)
            print(len(job_ids))

            with Pool(cpu_count()) as p:
                files = p.map(get_job_description, job_ids)            

        else:
            print(f"Failed to retrieve the URL. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


    start += 25

