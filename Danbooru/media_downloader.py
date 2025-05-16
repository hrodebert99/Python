import datetime
import time
import requests
import os

search_tags = input("Enter search tags: ")
include_tags = input("Enter include tags: ").split()
exclude_tags = input("Enter exclude tags: ").split()

download_folder_path = f".\\{search_tags}"
media_types = ["jpg", "png"]

if not os.path.exists(download_folder_path):
    os.makedirs(download_folder_path)

log_filename = f'.\\{search_tags}\\{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.log'

def log(message, console_output = True):
    with open(log_filename, 'a', encoding='utf-8') as file:
        file.write(f'{message} \n')

    if console_output:
        print(message)

log(f"Enter search tags: {search_tags}", False)
log(f"Enter include tags: {include_tags if include_tags != [] else ''}", False)
log(f"Enter exclude tags: {exclude_tags if exclude_tags != [] else ''}", False)

page_count = 0

page = 1

time.sleep(1)
response = requests.get(f"https://danbooru.donmai.us/posts.json?tags={search_tags}&page={page}")
posts = response.json()

while posts != []:
    page_count += 1
    log(f"Page count: {page_count}")

    for post in posts:
        log({ "tag_string_character": post["tag_string_character"], "tag_string_copyright": post["tag_string_copyright"], "tag_string_meta": post["tag_string_meta"], "tag_string_general": post["tag_string_general"] })

    page += 1

    time.sleep(1)
    response = requests.get(f"https://danbooru.donmai.us/posts.json?tags={search_tags}&page={page}")
    posts = response.json()

page = 1
log(f"Page {page}/{page_count}")

response = requests.get(f"https://danbooru.donmai.us/posts.json?tags={search_tags}&page={page}")
posts = response.json()

while posts != []:
    log(f"Page {page}/{page_count}")
    
    for post in posts:
        log(f"Post ID: {post['id'] if 'id' in post else ''}, Post MD5: {post['md5'] if 'md5' in post else ''}", False)

        if post["file_ext"] not in media_types:
            log(f"    Is not a valid media type", False)

            continue

        if "file_url" not in post:
            log(f"    No file_url", False)

            continue

        is_exclude_tag_found = False

        for tag in exclude_tags:
            if tag in post["tag_string"]:
                is_exclude_tag_found = True
                
                break

        if is_exclude_tag_found:
            log(f"    Exclude tag found", False)

            continue

        is_include_tag_found = True

        for tag in include_tags:
            if tag not in post["tag_string"]:
                is_include_tag_found = False
                
                break

        if not is_include_tag_found:
            log(f"    Include tag not found", False)

            continue

        post = {
            "id": post["id"],
            "file_ext": post["file_ext"],
            "tag_string_general": post["tag_string_general"].replace(" ", ", ").replace("_", " ").replace("(", "\\(").replace(")", "\\)"),
            "tag_string_character": post["tag_string_character"].replace(" ", ", ").replace("_", " ").replace("(", "\\(").replace(")", "\\)"),
            "tag_string_copyright": post["tag_string_copyright"].replace(" ", ", ").replace("_", " ").replace("(", "\\(").replace(")", "\\)"),
            "tag_string_artist": post["tag_string_artist"].replace(" ", ", ").replace("_", " ").replace("(", "\\(").replace(")", "\\)"),
            "tag_string_meta": post["tag_string_meta"].replace(" ", ", ").replace("_", " ").replace("(", "\\(").replace(")", "\\)"),
            "file_url": post["file_url"],
            "md5": post["md5"] if "md5" in post else None
        }
        
        if post["md5"] == None:
            file_name = post["id"]
        else:
            file_name = post["md5"]

        with open(f"{download_folder_path}\\{file_name}.txt", "w") as file:
            file.write(f"{post['tag_string_character']}, {post['tag_string_copyright']}, {post['tag_string_meta']}, {post['tag_string_general']}")

            log(f"    Downloaded {file_name}.txt", False)
        
        time.sleep(1)
        response = requests.get(post["file_url"], stream = True)

        if response.status_code == 200:
            with open(f"{download_folder_path}\\{file_name}.{post['file_ext']}", "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
                
            log(f"    Downloaded {file_name}.{post['file_ext']}", False)
    
    page += 1

    time.sleep(1)
    response = requests.get(f"https://danbooru.donmai.us/posts.json?tags={search_tags}&page={page}")
    posts = response.json()

log("Download complete")
