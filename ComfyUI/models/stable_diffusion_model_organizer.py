import glob
import time
import hashlib
import requests
import os

print('Stable Diffusion Model Organizer')
print('Getting all models in current directory.')

models = []

for extension in ['*.safetensors']:
    for filename in glob.glob(extension):
        models.append({'filename': filename})

print(f'{len(models)} models found.')
print('Starting model organization in 3 seconds. To cancel it, press CTRL + C.')

time.sleep(3 - 1)

for index, model in enumerate(models):
    time.sleep(1)

    print(f'{index + 1}/{len(models)} {model['filename']}')

    hasher = hashlib.sha256()

    with open(model['filename'], 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            hasher.update(chunk)
    
    model['hash'] = hasher.hexdigest()

    print(f'    SHA256: {model['hash']}')

    response = requests.get(f'https://civitai.com/api/v1/model-versions/by-hash/{model['hash']}')

    # TODO: Response code can be other than 200 or 404. If it is, raise an exception.
    
    if response.status_code == 404:
        print('    [404] Model not found on Civitai.')

        if os.path.exists('.\\_not_found'):
            os.makedirs('.\\_not_found')
        
        try:
            os.rename(model['filename'], f'.\\_not_found\\{model['filename']}')

            print(f'    [200] Model has been moved to .\\_not_found.')
        except FileExistsError:
            print('    [409] Model duplicate found.')

        continue
    else:
        model_version = response.json()

    model['id'] = model_version['modelId']
    model['version'] = model_version['id']
    model['base_model'] = model_version['baseModel']
    model['type'] = model_version['model']['type']

    response = requests.get(f'https://civitai.com/api/v1/models/{model['id']}')

    # TODO: Response code can be other than 200 or 404. If it is, raise an exception.

    _model = response.json()

    if 'creator' not in _model:
        model['creator'] = '_deleted'
    else:
        model['creator'] = _model['creator']['username']
    
    print(f'    AIR: {model['id']}@{model['version']} | Type: {model['type']} | Base Model: {model['base_model']} | Creator: {model['creator']}')

    if model['type'] not in ['Checkpoint', 'DoRA', 'LoCon', 'LORA', 'TextualInversion', 'VAE']:
        print('    [404] Model type not found.')

        continue

    if model['type'] == 'Checkpoint':
        new_folder_path = f'.\\checkpoints\\{model['base_model']}\\{model['creator']}'
    elif model['type'] in ['DoRA', 'LoCon', 'LORA']:
        new_folder_path = f'.\\loras\\{model['base_model']}\\{model['creator']}'
    elif model['type'] == 'TextualInversion':
        new_folder_path = f'.\\embeddings\\{model['base_model']}\\{model['creator']}'
    elif model['type'] == 'VAE':
        new_folder_path = f'.\\vae\\{model['base_model']}\\{model['creator']}'
    
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)

    try:
        os.rename(model['filename'], f'{new_folder_path}\\{model['filename']}')
        
        print(f'    [200] Model has been moved to {new_folder_path}')
    except FileExistsError:
        print('    [409] Model duplicate found')

        continue

print('Model organization completed.')
