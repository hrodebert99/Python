import json
import os
import requests
import time
page = 1
tags = 'hatsune_miku'
os.mkdir(tags)
response = requests.get(f'https://danbooru.donmai.us/posts.json?page={page}&tags={tags}')
images = json.loads(response.text)
while not images == []:
    for image in images:
        file_ext = image['file_ext']
        if file_ext in ['mp4']:
            continue
        md5 = image['md5']
        tag_string = image['tag_string'].replace(' ', ', ')
        with open(f'{tags}\\{md5}.txt', 'w') as file:
            file.write(tag_string)
        for variant in image['media_asset']['variants']:
            if variant['type'] == 'original':
                image_url = variant['url']
        response = requests.get(image_url)
        image = response.content
        with open(f'{tags}\\{md5}.{file_ext}', 'wb') as file:
            file.write(image)
    time.sleep(1)
    page += 1
    response = requests.get(f'https://danbooru.donmai.us/posts.json?page={page}&tags={tags}')
    images = json.loads(response.text)
