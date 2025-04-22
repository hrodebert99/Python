import datetime
import json
import os
import requests
import time

class Logger:
    filename = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.log'

    def __init__(self, value):
        print(value)
        with open(self.filename, 'a') as file:
            file.write(f'{value}\n')

class DanbooruImageDownloader:
    def __init__(self, included_tags, excluded_tags):
        self.included_tags = included_tags
        self.excluded_tags = excluded_tags.split(' ') if not excluded_tags == '' else []
        self.image_download_folder_path = self.included_tags
        page = 1
        allowed_image_types = ['jpg', 'png']
        Logger(f'Page {page}')
        posts = Danbooru.get_posts(self.included_tags, self.excluded_tags, page, allowed_image_types)
        while not posts == []:
            for post in posts:
                Logger(f'    {post.id} {post.tag_string_character}')
                post.download(self.image_download_folder_path)
            time.sleep(1)
            page += 1
            Logger(f'Page {page}')
            posts = Danbooru.get_posts(self.included_tags, self.excluded_tags, page, allowed_image_types)

class Danbooru:
    @staticmethod
    def get_posts(included_tags, excluded_tags, page, allowed_image_types):
        response = requests.get(f'https://danbooru.donmai.us/posts.json?tags={included_tags}&page={page}')
        posts_json = json.loads(response.text)
        posts = []
        for post_json in posts_json:
            if not post_json['file_ext'] in allowed_image_types:
                continue
            if not 'file_url' in post_json:
                continue
            for tag in excluded_tags:
                if tag in post_json['tag_string']:
                    break
            else:
                post = DanbooruPost(post_json)
                posts.append(post)
        return posts
    
    @staticmethod
    def format_tag_string(tag_string):
        tag_string = tag_string.replace(' ', ', ')
        tag_string = tag_string.replace('_', ' ')
        return tag_string

class DanbooruPost:
    def __init__(self, post_json):
        self.id = post_json['id']
        self.md5 = post_json['md5'] if 'md5' in post_json else None
        self.file_ext = post_json['file_ext']
        self.tag_string_general = Danbooru.format_tag_string(post_json['tag_string_general'])
        self.tag_string_character = Danbooru.format_tag_string(post_json['tag_string_character'])
        self.tag_string_copyright = Danbooru.format_tag_string(post_json['tag_string_copyright'])
        self.file_url = post_json['file_url']
    
    def download(self, image_download_folder_path):
        if not os.path.exists(image_download_folder_path):
            os.mkdir(image_download_folder_path)
        with open(f'{image_download_folder_path}\\{self.md5 if not self.md5 == None else self.id}.txt', 'w') as file:
            file.write(f'{self.tag_string_character}, {self.tag_string_copyright}, {self.tag_string_general}')
        response = requests.get(self.file_url)
        image = response.content
        with open(f'{image_download_folder_path}\\{self.md5 if not self.md5 == None else self.id}.{self.file_ext}', 'wb') as file:
            file.write(image)

if __name__ == '__main__':
    included_tags = input('Included tags: ')
    excluded_tags = input('Excluded tags: ')
    DanbooruImageDownloader(included_tags, excluded_tags)
