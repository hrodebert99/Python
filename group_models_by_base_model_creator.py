import datetime
import glob
import hashlib
import json
import os
import requests
import time

log_filename = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")}.log'

class ModelOrganizer:
    extensions = ['*.safetensors']
    initial_delay = 3
    iteration_delay = 1
    type_paths = {
        'Checkpoint': 'checkpoints',
        'DoRA': 'loras',
        'LoCon': 'loras',
        'LORA': 'loras',
        'TextualInversion': 'embeddings',
        'VAE': 'vae'
    }
    
    def __init__(self):
        Logger('Civitai Model Organizer')

        models = self.get_all_models()

        Logger(f'{len(models)} model(s) found.')
        Logger(f'Starting in {self.initial_delay} seconds. To cancel it, press CTRL+C.')

        time.sleep(self.initial_delay - self.iteration_delay)

        for index, model in enumerate(models):
            time.sleep(self.iteration_delay)

            Logger(f'{index + 1}/{len(models)} {model.filename}')
            Logger(f'    AIR: {model.id}@{model.version} | SHA256: {model.hash} | Type: {model.type} | Base Model: {model.base_model} | Creator: {model.creator}')

            if not model.type in self.type_paths.keys():
                Logger(f'    [404] Model type not found.')

                continue
            
            new_folder = f'{self.type_paths[model.type]}\\{model.base_model}\\{model.creator}'

            if not os.path.exists(new_folder):
                os.makedirs(new_folder)
            
            try:
                os.rename(model.filename, f'{new_folder}\\{model.filename}')
            except FileExistsError:
                Logger(f'    [409] Model duplicate found.')
        
        Logger('Process completed.')
    
    def get_all_models(self):
        models = []

        Logger('Getting all models in the current directory...')

        for extension in self.extensions:
            for model in glob.glob(extension):
                model = Model(model)

                if (model.id == None or
                    model.version == None or
                    model.base_model == None or
                    model.type == None or
                    model.creator == None):
                    continue

                models.append(model)

        return models



class Logger:
    def __init__(self, value):
        print(value)

        with open(log_filename, 'a', encoding = 'utf-8') as file:
            file.write(f'{value}\n')

class Model:
    def __init__(self, filename):
        self.filename = filename
        self.hash = self.calculate_hash(self.filename)
        self.id = None
        self.version = None
        self.base_model = None
        self.type = None
        self.creator = None
        
        model_version = Civitai().get_model_version(self.filename, self.hash)

        if not model_version == {}:
            self.id = model_version['modelId']
            self.version = model_version['id']
            self.base_model = model_version['baseModel']
            self.type = model_version['model']['type']

            model = Civitai().get_model(self.id)

            if 'creator' in model:
                self.creator = model['creator']['username']
            else:
                self.creator = '_deleted'

    def calculate_hash(self, filename):
        hasher = hashlib.sha256()

        with open(filename, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b''):
                hasher.update(chunk)
        
        hash = hasher.hexdigest()

        return hash

class Civitai:
    not_found_folder = '_not_found'

    def get_model_version(self, filename, hash):
        Logger(f'File: {filename} | SHA256: {hash}')

        response = requests.get(f'https://civitai.com/api/v1/model-versions/by-hash/{hash}')

        if response.status_code == 404:
            Logger('    [404] Model not found.')
        
            if not os.path.exists(self.not_found_folder):
                os.makedirs(self.not_found_folder)
            
            try:
                os.rename(filename, f'{self.not_found_folder}\\{filename}')
            except FileExistsError:
                Logger(f'    [409] Model duplicate found.')

            Logger(f'    [200] Model has been moved to {self.not_found_folder}')

            return {}
        
        model_version = json.loads(response.text)

        return model_version

    def get_model(self, id):
        response = requests.get(f'https://civitai.com/api/v1/models/{id}')
        model = json.loads(response.text)
        
        return model

if __name__ == '__main__':
    ModelOrganizer()
