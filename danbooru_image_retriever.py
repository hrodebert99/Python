import datetime
import json
import os
import requests
import time

def get_images(page, tags):
    response = requests.get(f'https://danbooru.donmai.us/posts.json?page={page}&tags={tags}')
    return json.loads(response.text)

def download_image(url, name = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')):
    response = requests.get(url)
    image = response.content
    
    with open(name, 'wb') as file:
        file.write(image)

page = 1
tags = 'pallas_(arknights)'

print('Process started.')

os.mkdir(tags)

images = get_images(page, tags)

tag_string_count = {}

while not images == []:
    print(f'    Page {page}')

    for image in images:
        file_ext = image['file_ext']
        
        if file_ext in ['mp4']:
            continue
        
        filename = image['md5'] if 'md5' in image else datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        
        tag_string = image['tag_string'].split(' ')
        
        for tag in tag_string:
            tag_string_count[tag] = tag_string_count.get(tag, 0) + 1
        
        tag_string = image['tag_string'].replace(' ', ', ')
        
        with open(f'{tags}\\{filename}.txt', 'w') as file:
            file.write(tag_string)

        if not 'variants' in image['media_asset']:
            continue
        
        for variant in image['media_asset']['variants']:
            if variant['type'] == 'original':
                image_url = variant['url']
        
        download_image(image_url, f'{tags}\\{filename}.{file_ext}')
    
    time.sleep(1)
    
    page += 1
    images = get_images(page, tags)

tag_string_count = sorted(tag_string_count.items(), key = lambda item: item[1], reverse = True)
tag_string = [key for key, value in tag_string_count]
tag_string = ', '.join(tag_string)

with open(f'{tags}/_tags.txt', 'w') as file:
    file.write(tag_string)

print('Process completed.')
