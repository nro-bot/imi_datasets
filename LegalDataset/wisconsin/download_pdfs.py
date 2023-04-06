# 06 April 2023
# nrobot

# Script to automatically (currently I pulled with a GUI tool) download all PDFs
# in massage category from Wisconsin site

# For ethical reasons, want to avoid sharing entire set of PDFs
# Instead provide script to replicate dataset.


import requests
from bs4 import BeautifulSoup
from pathlib import Path

professions = {46: 'Massage Therapist Or Bodyworker',
               146: 'Massage Therapist or Bodywork Therapist',
               47: 'Massage Therapist-No longer applicable-see #046'}

base_url = 'https://online.drl.wi.gov/orders/PrinterFriendlyPage.aspx?ctId='

all_urls = []
for ID in professions.keys():
    print(f'Retrieving URLs for {ID}')
    soup = BeautifulSoup(requests.get(base_url + ID).text, 'html.parser')
    urls = [link['href'] for link in soup('a')]
    print(
        f'Retrieved {len(urls)} URLs for profession {ID}: {professions[ID}')
    #[(link['href'] if link['href'] else None) for link in soup('a')]

with open('./nogit_data/wisconsin_pdf_urls.txt', 'w') as f:
    f.write('\n'.join(all_urls))


pdf_base_url = 'https://online.drl.wi.gov/_'

for url in all_urls:
    r = requests.get('https://api.github.com/events')
    #with open(f'./nogit_data/{a
        #https://online.drl.wi.gov/decisions/
