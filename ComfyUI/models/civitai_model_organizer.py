import datetime
import glob
import hashlib
import json
import os
import requests
import time

class ModelOrganizer:
    allowed_model_extensions = ['*.safetensors']
    initial_run_delay = 3
    iteration_loop_delay = 1
    model_type_folder_paths = {
        'Checkpoint': 'checkpoints',
        'DoRA': 'loras',
        'LoCon': 'loras',
        'LORA': 'loras',
        'TextualInversion': 'embeddings',
        'VAE': 'vae'
    }
    
    def __init__(self):
        Logger('Civitai Model Organizer')
        Logger('Getting all models in the current directory.')
        models = self.get_all_models()
        Logger(f'{len(models)} models found.')
        Logger(f'Starting the model organization in {self.initial_run_delay} seconds. To cancel it, press CTRL+C anytime.')
        time.sleep(self.initial_run_delay - self.iteration_loop_delay)
        for index, model in enumerate(models):
            time.sleep(self.iteration_loop_delay)
            Logger(f'{index + 1}/{len(models)} {model.filename}')
            model.calculate_hash()
            Logger(f'    SHA256: {model.hash}')
            model_version = Civitai.get_model_version(model.hash)
            if model_version == {}:
                Logger('    [404] Model not found.')
                continue
            model.model_version(model_version)
            if model.id == None:
                Logger('    [404] Model not found.')
                continue
            model.model(Civitai.get_model(model.id))
            Logger(f'    AIR: {model.id}@{model.version} | Type: {model.type} | Base Model: {model.base_model} | Creator: {model.creator}')
            if not model.type in self.model_type_folder_paths.keys():
                Logger('    [404] Model type not found.')
                continue
            new_folder_path = f'{self.model_type_folder_paths[model.type]}\\{model.base_model}\\{model.creator}'
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
            try:
                os.rename(model.filename, f'{new_folder_path}\\{model.filename}')
                Logger(f'    [200] Model has been moved to {new_folder_path}')
            except FileExistsError:
                Logger('    [409] Model duplicate found')
        Logger('The model organization completed.')
    
    def get_all_models(self):
        models = []
        for extension in self.allowed_model_extensions:
            for filename in glob.glob(extension):
                model = Model(filename)
                models.append(model)
        return models

class Logger:
    filename = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.log'
    
    def __init__(self, value):
        print(value)
        with open(self.filename, 'a', encoding = 'utf-8') as file:
            file.write(f'{value}\n')

class Model:
    def __init__(self, filename):
        self.filename = filename
        self.hash = None
        self.id = None
        self.version = None
        self.base_model = None
        self.type = None
        self.creator = None
    
    def calculate_hash(self):
        hasher = hashlib.sha256()
        with open(self.filename, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b''):
                hasher.update(chunk)
        hash = hasher.hexdigest()
        self.hash = hash
    
    def model_version(self, model_version):
        if model_version == {}:
            return
        self.id = model_version['modelId']
        self.version = model_version['id']
        self.base_model = model_version['baseModel']
        self.type = model_version['model']['type']
    
    def model(self, model):
        if not 'creator' in model:
            self.creator = '_deleted'
            return
        self.creator = model['creator']['username']

class Civitai:
    @staticmethod
    def get_model_version(hash):
        response = requests.get(f'https://civitai.com/api/v1/model-versions/by-hash/{hash}')
        if not response.status_code in [200, 404]:
            Logger(f'ERROR {response.status_code}: {response.text}')
            raise Exception
        if response.status_code == 404:
            return {}
        model_version = json.loads(response.text)
        return model_version

    @staticmethod
    def get_model(id):
        response = requests.get(f'https://civitai.com/api/v1/models/{id}')
        if not response.status_code in [200, 404]:
            Logger(f'ERROR {response.status_code}: {response.text}')
            raise Exception
        model = json.loads(response.text)
        return model

if __name__ == '__main__':
    ModelOrganizer()
