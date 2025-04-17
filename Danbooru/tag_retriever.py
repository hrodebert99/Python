import json
import requests
import time

open('autocomplete.txt', 'w')

url = f'https://danbooru.donmai.us/tags.json?limit=1000&search[hide_empty]=yes&search[order]=count'
page = 0
response = requests.get(f'{url}&page={page}')
tags = json.loads(response.text)

while not tags == []:
    for index in range(len(tags)):
        with open('autocomplete.txt', 'a') as file:
            file.write(f'{tags[index]["name"]},{tags[index]["post_count"]}\n')
    
    print(f'Page {page} completed.')
    
    time.sleep(1)
    
    page += 1
    response = requests.get(f'{url}&page={page}')
    tags = json.loads(response.text)
