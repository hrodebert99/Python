import datetime
import glob
import hashlib
import json
import os
import requests
import time

log_filename = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")}.log'

class Logger:
    def __init__(self, value):
        with open(log_filename, 'a', encoding = 'utf-8') as file:
            file.write(f'{value}\n')

class Model:
    def __init__(self, filename):
        self.filename = filename
        self.hash = self.calculate_hash(self.filename)
        
        model_json = Civitai().get_model_by_hash(self.filename, self.hash)

        if model_json == {}:
            return

        self.id = model_json['modelId']
        self.version = model_json['id']
        self.base_model = model_json['baseModel']
        self.type = model_json['model']['type']

        if 'creator' in model_json:
            self.creator = model_json['creator']['username']
        else:
            self.creator = '_deleted'

    def calculate_hash(self, filename):
        hasher = hashlib.sha256()

        with open(filename, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b''):
                hasher.update(chunk)
        
        return hasher.hexdigest()

class Civitai:
    def __init__(self):
        self.unknown_model_folder = 'others'

    def get_model_by_hash(self, filename, hash):
        Logger(f'    SHA256: {hash}')

        response = requests.get(f'https://civitai.com/api/v1/model-versions/by-hash/{hash}')

        if response.status_code == 404:
            Logger('            [404] Model not found.')
        
            if not os.path.exists(self.unknown_model_folder):
                os.makedirs(self.unknown_model_folder)
            
            try:
                os.rename(filename, f'{self.unknown_model_folder}\\{filename}')
            except FileExistsError:
                Logger(f'                [409] Model duplicate found.')

            Logger(f'                [200] Model has been moved to {self.unknown_model_folder}')

            model_json = {}
        else:
            model_json = json.loads(response.text)

        return model_json

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
    
    def get_all_models(self):
        models = []

        Logger('    Searching for models...')

        for extension in self.extensions:
            for model in glob.glob(extension):
                model = Model(model)

                if (model.id == 'undefined' 
                    or model.version == 'undefined' 
                    or model.base_model == 'undefined' 
                    or model.type == 'undefined' 
                    or model.creator == 'undefined'):
                    continue

                models.append(model)

        return models
    
    def run(self):
        Logger('Civitai Model Organizer')

        models = self.get_all_models()

        Logger(f'    {len(models)} model(s) found.')
        Logger(f'    Starting in {self.initial_delay} seconds. To cancel it, press CTRL+C.')

        time.sleep(self.initial_delay - self.iteration_delay)

        for index, model in enumerate(models):
            time.sleep(self.iteration_delay)

            Logger(f'        {index + 1}/{len(models)} {model.filename}')
            Logger(f'        AIR: {model.id}@{model.version} | SHA256: {model.hash} | Type: {model.type} | Base Model: {model.base_model} | Creator: {model.creator}')

            if not model.type in self.type_paths.keys():
                Logger(f'            [404] Model type not found.')

                continue
            
            new_folder_path = f'{self.type_paths[model.type]}\\{model.base_model}\\{model.creator}'

            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
            
            try:
                os.rename(model.filename, f'{new_folder_path}\\{model.filename}')
            except FileExistsError:
                Logger(f'            [409] Model duplicate found.')
        
        Logger('    Process completed.')

if __name__ == '__main__':
    model_organizer = ModelOrganizer()
    model_organizer.run()
