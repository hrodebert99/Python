import datetime
import glob
import hashlib
import json
import os
import requests
import time

log_file = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")}.log'

def log(value):
    if not os.path.exists(f'.\\{log_file}'):
        open(log_file, 'w', encoding = 'utf-8')
    
    with open(log_file, 'a', encoding = 'utf-8') as file:
        file.write(f'{value} \n')
    
    print(value)

models = []

for extension in ('*.ckpt', '*.pt', '*.safetensors'):
    for model in glob.glob(extension):
        models.append(model)

count = len(models)

model_type_paths = {
    'Checkpoint': 'checkpoints',
    'LoCon': 'loras',
    'LORA': 'loras',
    'TextualInversion': 'embeddings',
    'VAE': 'vae'
}

log( 'Civitai Model Organizer')
log(f'    {count} model(s) found.')
log( '    Starting the model organization process in 3 seconds.')
log( '    To cancel the process, press CTRL+C.')

time.sleep(3 - 1)

for index, model_file in enumerate(models):
    time.sleep(1)

    log( '')
    log(f'{index + 1}/{count} {model_file}')

    hash = hashlib.sha256()

    with open(model_file, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            hash.update(chunk)

    hash = hash.hexdigest()
    
    log(f'    SHA256: {hash}')

    response = requests.get(f'https://civitai.com/api/v1/model-versions/by-hash/{hash}')

    # print(response)

    if response.status_code == 404:
        log('    [404] Not found in Civitai.')

        folder = 'others'

        if not os.path.exists(folder):
            os.makedirs(folder)

            log(f'    [] Created {folder} folder.')

        model_path = f'{folder}\\{model_file}'

        if os.path.exists(model_path):
            log(f'    [] Found a duplicate in {folder}.')
            log( '    Skipped.')
        
        try:
            os.rename(model_file, model_path)
        except KeyboardInterrupt:
            log('    [] Process interrupted.')
            log('    Stopped.')

            break

        log(f'    [] Moved to {model_path}.')

        continue

    response = json.loads(response.text)

    model = {
        'id': response['modelId'],
        'version': response['id'],
        'base_model': response['baseModel'],
        'type': response['model']['type']
    }

    response = requests.get(f'https://civitai.com/api/v1/models/{model["id"]}')

    # print(response)
    
    response = json.loads(response.text)

    if 'creator' in response:
        model['creator'] = response['creator']['username']
    else:
        model['creator'] = '_deleted'
    
    log(f'    {model["id"]}@{model["version"]} | {model["type"]} | {model["base_model"]} | {model["creator"]}')

    if not model['type'] in model_type_paths.keys():
        log(f'    [] Not a type of {", ".join(model_type_paths.keys())}.')
        log( '    Skipped.')

        continue

    model['path'] = f'{model_type_paths[model["type"]]}\\{model["base_model"]}\\{model["creator"]}\\{model_file}'

    folder = os.path.dirname(model['path'])

    if not os.path.exists(folder):
        os.makedirs(folder)

        log(f'    [] Created {folder} folder.')
    
    if os.path.exists(model['path']):
        log(f'    [] Found a duplicate in {folder}.')
        log( '    Skipped.')
    
    try:
        os.rename(model_file, model['path'])
    except KeyboardInterrupt:
        log('    [] Process interrupted.')
        log('    Stopped.')

        break

    log(f'    [] Moved to {model["path"]}.')

log('')
log('Process completed.')
