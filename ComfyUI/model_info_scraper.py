import sqlite3
import os
import hashlib
import requests

connection = sqlite3.connect('stable_diffusion.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS models (
        sha256 TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        id INTEGER NOT NULL,
        version INTEGER NOT NULL,
        base_model TEXT NOT NULL,
        type TEXT NOT NULL,
        creator TEXT NOT NULL
    )
''')

cursor.execute("SELECT * FROM models")
models = cursor.fetchall()

model_types = []

for description in cursor.description:
    model_types.append(description[0])

_models = []

for model in models:
    model = dict(zip(model_types, model))
    
    _models.append(model)

for root, folders, files in os.walk('.\\models'):
    for filename in files:
        is_in_database = False

        for model in _models:
            if filename == model['filename']:
                is_in_database = True

                break
        
        if is_in_database:
            print(f'{filename} already in database.')
            
            continue

        hasher = hashlib.sha256()

        with open(f'{root}\\{filename}', 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b''):
                hasher.update(chunk)
        
        model = {
            'sha256': hasher.hexdigest()
        }

        cursor.execute("SELECT * FROM models WHERE sha256 = ?", (model['sha256'],))
        row = cursor.fetchone()

        if row is not None:
            continue

        response = requests.get(f'https://civitai.com/api/v1/model-versions/by-hash/{model['sha256']}')

        if response.status_code == 404:
            model['id'] = -1
            model['version'] = -1
            model['base_model'] = None
            model['type'] = None
            model['creator'] = None
        else:
            try:
                model_version = response.json()
            except requests.exceptions.JSONDecodeError:
                print(f'    {response.status_code}: {response.text}.')
                continue

            model['id'] = model_version['modelId']
            model['version'] = model_version['id']
            model['base_model'] = model_version['baseModel']
            model['type'] = model_version['model']['type']

            response = requests.get(f'https://civitai.com/api/v1/models/{model['id']}')

            _model = response.json()

            if 'creator' not in _model:
                model['creator'] = None
            else:
                model['creator'] = _model['creator']['username']
        
        cursor.execute("INSERT INTO models (sha256, filename, id, version, base_model, type, creator) VALUES (?, ?, ?, ?, ?, ?, ?)", (model['sha256'], filename, model['id'], model['version'], model['base_model'] if model['base_model'] != None else 'null', model['type'] if model['type'] != None else 'null', model['creator'] if model['creator'] != None else 'null'))

        connection.commit()
        
        # cursor.execute("SELECT * FROM models")
        # rows = cursor.fetchall()

        # print(rows)

connection.close()
