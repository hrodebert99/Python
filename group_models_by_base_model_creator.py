import datetime
import glob
import hashlib
import json
import os
import requests
import time

log_file = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")}.log'

def log(value):
    with open(log_file, 'a', encoding = 'utf-8') as file:
        file.write(f'{value} \n')
    
    print(value)

model_list = [model for extension in ('*.ckpt', '*.pt', '*.safetensors') for model in glob.glob(extension)]
model_length = len(model_list)
model_type_path_dictionary = {
    'Checkpoint': 'checkpoints',
    'DoRA': 'loras',
    'LoCon': 'loras',
    'LORA': 'loras',
    'TextualInversion': 'embeddings',
    'VAE': 'vae'
}

log( 'Civitai Model Organizer')
log(f'    {model_length} model(s) found.')
log( '    Starting the process in 3 seconds.')
log( '    To cancel it, press CTRL+C.')

time.sleep(3 - 1)

for index, model_file in enumerate(model_list):
    time.sleep(1)

    log( '')
    log(f'{index + 1}/{model_length} {model_file}')

    hasher = hashlib.sha256()

    with open(model_file, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            hasher.update(chunk)

    model_hash = hasher.hexdigest()
    
    log(f'    SHA256: {model_hash}')

    response = requests.get(f'https://civitai.com/api/v1/model-versions/by-hash/{model_hash}')

    if response.status_code == 404:
        log('    [404] Not found in Civitai.')

        if not os.path.exists('others'):
            os.makedirs('others')

            log(f'    [] Created others folder.')
        
        try:
            os.rename(model_file, f'others\\{model_file}')
        except FileExistsError:
            log(f'    [] Found a duplicate in others.')
            log( '    Skipped.')

            continue
        except KeyboardInterrupt:
            log('    [] Process interrupted.')
            log('    Stopped.')

            break

        log(f'    [] Moved to others\\{model_file}.')

        continue

    response = json.loads(response.text)

    model = {
        'id': response['modelId'],
        'version': response['id'],
        'base_model': response['baseModel'],
        'type': response['model']['type']
    }

    response = requests.get(f'https://civitai.com/api/v1/models/{model["id"]}')
    response = json.loads(response.text)

    if 'creator' in response:
        model['creator'] = response['creator']['username']
    else:
        model['creator'] = '_deleted'
    
    log(f'    {model["id"]}@{model["version"]} | {model["type"]} | {model["base_model"]} | {model["creator"]}')

    if not model['type'] in model_type_path_dictionary.keys():
        log(f'    [] Not a type of {", ".join(model_type_path_dictionary.keys())}.')
        log( '    Skipped.')

        continue

    model['path'] = f'{model_type_path_dictionary[model["type"]]}\\{model["base_model"]}\\{model["creator"]}\\{model_file}'

    if not os.path.exists(os.path.dirname(model["path"])):
        os.makedirs(os.path.dirname(model["path"]))

        log(f'    [] Created {os.path.dirname(model["path"])} folder.')
    
    try:
        os.rename(model_file, model["path"])
    except FileExistsError:
        log(f'    [] Found a duplicate in {model["path"]}.')
        log( '    Skipped.')

        continue
    except KeyboardInterrupt:
        log('    [] Process interrupted.')
        log('    Stopped.')

        break

    log(f'    [] Moved to {model["path"]}.')

log('')
log('Process completed.')
