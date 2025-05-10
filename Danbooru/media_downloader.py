import requests
import json
import os
import time

search_tags = input('Search tags: ')
include_tags = input('Include tags: ').split(' ')
exclude_tags = input('Exclude tags: ').split(' ')

download_folder_path = f'.\\{search_tags}'
allowed_media_types = ['jpg', 'png']

page = 1
print(f'Page {page}')

time.sleep(1)
response = requests.get(f'https://danbooru.donmai.us/posts.json?tags={search_tags}&page={page}')
posts_json = json.loads(response.text)

while posts_json != []:
    for post_json in posts_json:
        if post_json['file_ext'] not in allowed_media_types:
            continue

        if 'file_url' not in post_json:
            continue

        is_exclude_tag_found = False
        
        for tag in exclude_tags:
            if tag in post_json['tag_string']:
                is_exclude_tag_found = True
                break
        
        if is_exclude_tag_found:
            continue
        
        is_include_tag_found = True

        for tag in include_tags:
            if tag not in post_json['tag_string']:
                is_include_tag_found = False
                break
        
        if not is_include_tag_found:
            continue

        post = {}
        post['id'] = post_json['id']
        post['file_ext'] = post_json['file_ext']
        post['tag_string_general'] = post_json['tag_string_general'].replace(' ', ', ').replace('_', ' ').replace('(', '\\(').replace(')', '\\)')
        post['tag_string_character'] = post_json['tag_string_character'].replace(' ', ', ').replace('_', ' ').replace('(', '\\(').replace(')', '\\)')
        post['tag_string_copyright'] = post_json['tag_string_copyright'].replace(' ', ', ').replace('_', ' ').replace('(', '\\(').replace(')', '\\)')
        post['tag_string_artist'] = post_json['tag_string_artist'].replace(' ', ', ').replace('_', ' ').replace('(', '\\(').replace(')', '\\)')
        post['file_url'] = post_json['file_url']

        if 'md5' in post_json:
            post['md5'] = post_json['md5']
        else:
            post['md5'] = None

        print(f'{post_json['id']}')
        
        if not os.path.exists(download_folder_path):
            os.mkdir(download_folder_path)
        
        if post['md5'] != None:
            filename = post['md5']
        else:
            filename = post['id']

        with open(f'.\\{download_folder_path}\\{filename}.txt', 'w') as file:
            file.write(f'{post['tag_string_character']}, {post['tag_string_copyright']}, {post['tag_string_artist'}, {post['tag_string_general']}')
        
        time.sleep(1)
        response = requests.get(post['file_url'])
        image = response.content

        with open(f'.\\{download_folder_path}\\{filename}.{post['file_ext']}', 'wb') as file:
            file.write(image)
    
    page += 1
    print(f'Page {page}')

    time.sleep(1)
    response = requests.get(f'https://danbooru.donmai.us/posts.json?tags={search_tags}&page={page}')
    posts_json = json.loads(response.text)
