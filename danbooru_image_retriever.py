import json
import os
import requests

class Danbooru:
    def get_posts(include_tags, exclude_tags = [], page = 1):
        url = f'https://danbooru.donmai.us/posts.json?tags={include_tags}&page={page}'
        response = requests.get(url).text
        posts_json = json.loads(response)
        posts = []
        for post in posts_json:
            if not post['file_ext'] in ['jpg', 'png']:
                continue

            if not 'file_url' in post:
                continue

            for tag in exclude_tags:
                if tag in post['tag_string']:
                    break
            else:
                print(post['tag_string_character'])

                post = DanbooruPost(post)
                posts.append(post)
        return posts
    
    def format_tag_string(tag_string):
        tag_string = tag_string.replace(' ', ', ')
        tag_string = tag_string.replace('_', ' ')
        tag_string = tag_string.replace('(', '\\(')
        tag_string = tag_string.replace(')', '\\)')
        return tag_string

class DanbooruPost:
    def __init__(self, post):
        self.id = post['id']
        self.md5 = post['md5'] if 'md5' in post else None
        self.file_ext = post['file_ext']
        self.tag_string_general = Danbooru.format_tag_string(post['tag_string_general'])
        self.tag_string_character = Danbooru.format_tag_string(post['tag_string_character'])
        self.tag_string_copyright = Danbooru.format_tag_string(post['tag_string_copyright'])
        self.file_url = post['file_url']
        
    def download_original(self, save_folder):
        print(f'Downloading {post.id}')

        url = post.file_url
        response = requests.get(url)
        image = response.content
        
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)
        
        filename = f'{save_folder}\\{self.md5 if not self.md5 == None else self.id}.{self.file_ext}'
        
        with open(filename, 'wb') as file:
            file.write(image)

    def download_tag_string(self, save_folder):
        with open(f'{save_folder}\\{self.md5}.txt', 'w') as file:
            file.write(f'{self.tag_string_character}, {self.tag_string_copyright}, {self.tag_string_general}')

if __name__ == '__main__':
    include_tags = input('Include tags: ')
    exclude_tags = input('Exclude tags: ')
    exclude_tags = exclude_tags.split(' ') if not exclude_tags == '' else []
    save_folder = include_tags

    print('Process started.')
    
    page = 1
    print(f'Page {page}')
    posts = Danbooru.get_posts(include_tags, exclude_tags, page)

    while not posts == []:
        for post in posts:
            post.download_original(save_folder)
            post.download_tag_string(save_folder)
            
        page += 1
        print(f'Page {page}')
        posts = Danbooru.get_posts(include_tags, exclude_tags, page)

    print('Process completed.')
