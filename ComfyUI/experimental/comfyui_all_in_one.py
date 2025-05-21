import datetime
import sqlite3
import os
import hashlib
import time
import requests

log_filename = f'{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.log'

def log(message):
    with open(log_filename, 'a', encoding='utf-8') as file:
        file.write(f'{message} \n')

    print(message)

exclude_files = [
    '.\\models\\checkpoints\\put_checkpoints_here',
    '.\\models\\clip\\put_clip_or_text_encoder_models_here',
    '.\\models\\clip_vision\\put_clip_vision_models_here',
    '.\\models\\configs\\anything_v3.yaml',
    '.\\models\\configs\\v1-inference.yaml',
    '.\\models\\configs\\v1-inference_clip_skip_2.yaml',
    '.\\models\\configs\\v1-inference_clip_skip_2_fp16.yaml',
    '.\\models\\configs\\v1-inference_fp16.yaml',
    '.\\models\\configs\\v1-inpainting-inference.yaml',
    '.\\models\\configs\\v2-inference.yaml',
    '.\\models\\configs\\v2-inference_fp32.yaml',
    '.\\models\\configs\\v2-inference-v.yaml',
    '.\\models\\configs\\v2-inference-v_fp32.yaml',
    '.\\models\\configs\\v2-inpainting-inference.yaml',
    '.\\models\\controlnet\\put_controlnets_and_t2i_here',
    '.\\models\\diffusers\\put_diffusers_models_here',
    '.\\models\\diffusion_models\\put_diffusion_model_files_here',
    '.\\models\\embeddings\\put_embeddings_or_textual_inversion_concepts_here',
    '.\\models\\gligen\\put_gligen_models_here',
    '.\\models\\hypernetworks\\put_hypernetworks_here',
    '.\\models\\loras\\put_loras_here',
    '.\\models\\photomaker\\put_photomaker_models_here',
    '.\\models\\style_models\\put_t2i_style_model_here',
    '.\\models\\text_encoders\\put_text_encoder_files_here',
    '.\\models\\unet\\put_unet_files_here',
    '.\\models\\upscale_models\\put_esrgan_and_other_upscale_models_here',
    '.\\models\\vae\\put_vae_here',
    '.\\models\\vae_approx\\put_taesd_encoder_pth_and_taesd_decoder_pth_here',
    '.\\models\\vae_approx\\taef1_decoder.pth',
    '.\\models\\vae_approx\\taef1_encoder.pth',
    '.\\models\\vae_approx\\taesd_decoder.pth',
    '.\\models\\vae_approx\\taesd_encoder.pth',
    '.\\models\\vae_approx\\taesd3_decoder.pth',
    '.\\models\\vae_approx\\taesd3_encoder.pth',
    '.\\models\\vae_approx\\taesdxl_decoder.pth',
    '.\\models\\vae_approx\\taesdxl_encoder.pth',
    '.\\models\\clip_vision\\clip-vision_vit-h.safetensors',
    '.\\models\\clip_vision\\OpenCLIP-ViT-bigG-14.safetensors',
    '.\\models\\controlnet\\controlnet-union-sdxl-1.0.safetensors',
    '.\\models\\inpaint\\fooocus_inpaint_head.pth',
    '.\\models\\inpaint\\inpaint_v26.fooocus.patch',
    '.\\models\\inpaint\\MAT_Places512_G_fp16.safetensors',
    '.\\models\\ipadapter\\ip-adapter_sd15.bin',
    '.\\models\\ipadapter\\ip-adapter_sd15_light.bin',
    '.\\models\\ipadapter\\ip-adapter_sdxl.bin',
    '.\\models\\ipadapter\\ip-adapter_sdxl_vit-h.bin',
    '.\\models\\ipadapter\\ip-adapter_sdxl_vit-h.safetensors',
    '.\\models\\ipadapter\\ip-adapter-plus_sd15.bin',
    '.\\models\\ipadapter\\ip-adapter-plus_sdxl_vit-h.bin',
    '.\\models\\ipadapter\\ip-adapter-plus-face_sd15.bin',
    '.\\models\\ipadapter\\ip-adapter-plus-face_sdxl_vit-h.bin',
    '.\\models\\sams\\sam_vit_b_01ec64.pth',
    '.\\models\\upscale_models\\4x_NMKD-Superscale-SP_178000_G.pth',
    '.\\models\\upscale_models\\OmniSR_X2_DIV2K.safetensors',
    '.\\models\\upscale_models\\OmniSR_X3_DIV2K.safetensors',
    '.\\models\\upscale_models\\OmniSR_X4_DIV2K.safetensors',
    '.\\models\\upscale_models\\RealESRGAN_x4.pth',
    '.\\models\\model_directory_flattener.py',
    '.\\models\\stable_diffusion_model_organizer.py'
]

connection = sqlite3.connect('comfyui.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS models (
        hash TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL
    )
''')

# cursor.execute('SELECT * FROM models')
# models_in_database = cursor.fetchall()

# for index, model in enumerate(models_in_database):
#     models_in_database[index] = dict(zip([description[0] for description in cursor.description], model))

# for root, folders, files in os.walk('.\\models'):
#     for filename in files:
#         log(f'Processing {filename}...')

#         file_path = f'{root}\\{filename}'

#         if file_path in exclude_files:
#             log(f'    Excluded.')

#             continue

#         if file_path in [model['file_path'] for model in models_in_database]:
#             log(f'    Already in database.')

#             continue

#         hasher = hashlib.sha256()

#         with open(file_path, 'rb') as file:
#             for chunk in iter(lambda: file.read(4096), b''):
#                 hasher.update(chunk)
        
#         hash = hasher.hexdigest()

#         if hash in [model['hash'] for model in models_in_database]:
#             log(f'    Already in database.')

#             continue

#         cursor.execute('INSERT INTO models (hash, filename, file_path) VALUES (?, ?, ?)', (hash, filename, file_path))

#         connection.commit()

#         log(f'    Added to database.')

cursor.execute('SELECT * FROM models')
models_in_database = cursor.fetchall()

for index, model in enumerate(models_in_database):
    models_in_database[index] = dict(zip([description[0] for description in cursor.description], model))

for model in models_in_database:
    # time.sleep(1)

    model = model['file_path'].split('\\')

    if model[3] == '_not_found':
        log(model[2:4])
    else:
        log(model[2:5])

    # log(f'Processing {model['filename']}...')
    # log(f'    https://civitai.com/api/v1/model-versions/by-hash/{model['hash']}')

    # response = requests.get(f'https://civitai.com/api/v1/model-versions/by-hash/{model['hash']}')

    # TODO: Response code can be other than 200 or 404. If it is, raise an exception.

    # if response.status_code == 404:
    #     continue

connection.close()

##
# import glob
# import sqlite3
# import hashlib

# extensions = [
#     '*.safetensors'
# ]

# new_models = []

# for extension in extensions:
#     for filename in glob.glob(extension):
#         model = {
#             'sha256': None,
#             'filename': filename,
#             'id': None,
#             'version': None,
#             'base_model': None,
#             'type': None,
#             'creator': None
#         }

#         new_models.append(model)

# # log(new_models)
# log(f'{len(new_models)} new models found.')

# connection = sqlite3.connect('stable_diffusion.db')
# cursor = connection.cursor()

# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS models (
#         sha256 TEXT PRIMARY KEY,
#         filename TEXT NOT NULL,
#         id INTEGER NOT NULL,
#         version INTEGER NOT NULL,
#         base_model TEXT NOT NULL,
#         type TEXT NOT NULL,
#         creator TEXT NOT NULL
#     )
# ''')

# cursor.execute('SELECT sha256, filename FROM models')
# database_models = cursor.fetchall()

# for index, model in enumerate(database_models):
#     database_models[index] = { 'sha256': model[0], 'filename': model[1] }

# # log(database_models)
# log(f'{len(database_models)} models found in database.')

# for model in new_models:
#     hasher = hashlib.sha256()

#     with open(model['filename'], 'rb') as file:
#         for chunk in iter(lambda: file.read(4096), b''):
#             hasher.update(chunk)
    
#     model['sha256'] = hasher.hexdigest()

#     is_in_database = False

#     for _model in database_models:
#         if model['sha256'] == _model['sha256']:
#             is_in_database = True

#             break
    
#     if is_in_database:
#         log(f'{model['filename']} already in database.')

#         continue
##

##
# import glob
# import sqlite3
# import hashlib
# import requests

# def get_new_models():
#     new_models = []

#     for extension in ['*.safetensors']:
#         for filename in glob.glob(extension):
#             model = {
#                 'sha256': None,
#                 'filename': filename,
#                 'id': None,
#                 'version': None,
#                 'base_model': None,
#                 'type': None,
#                 'creator': None
#             }

#             new_models.append(model)

#     log(f'{len(new_models)} new models found.')

#     return new_models

# def connect_to_database():
#     connection = sqlite3.connect('stable_diffusion.db')
    
#     cursor = connection.cursor()
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS models (
#             sha256 TEXT PRIMARY KEY,
#             filename TEXT NOT NULL,
#             id INTEGER NOT NULL,
#             version INTEGER NOT NULL,
#             base_model TEXT NOT NULL,
#             type TEXT NOT NULL,
#             creator TEXT NOT NULL
#         )
#     ''')

#     return connection, cursor

# def get_stored_models_from_database(cursor):
#     cursor.execute('SELECT * FROM models')
#     stored_models = cursor.fetchall()

#     for index, model in enumerate(stored_models):
#         stored_models[index] = dict(zip([description[0] for description in cursor.description], model))

#     log(f'{len(stored_models)} models found in database.')

#     return stored_models

# def is_exist_in_database(model, stored_models):
#     duplicate_count = 0

#     for _model in stored_models:
#         if model['filename'] == _model['filename']:
#             duplicate_count += 1
    
#     if duplicate_count == 1:
#         return True, model
    
#     hasher = hashlib.sha256()

#     with open(model['filename'], 'rb') as file:
#         for chunk in iter(lambda: file.read(4096), b''):
#             hasher.update(chunk)
    
#     model['sha256'] = hasher.hexdigest()
    
#     if duplicate_count >= 2:
#         if model['sha256'] in [_model['sha256'] for _model in stored_models]:
#             return True, model
    
#     return False, model

# def get_model_info(model):
#     response = requests.get(f'https://civitai.com/api/v1/model-versions/by-hash/{model['sha256']}')

#     # TODO: Response code can be other than 200 or 404. If it is, raise an exception.

#     if response.status_code != 404:
#         model_version = response.json()

#         model['id'] = model_version['modelId']
#         model['version'] = model_version['id']
#         model['base_model'] = model_version['baseModel']
#         model['type'] = model_version['model']['type']

#         response = requests.get(f'https://civitai.com/api/v1/models/{model['id']}')

#         # TODO: Response code can be other than 200 or 404. If it is, raise an exception.

#         _model = response.json()

#         if 'creator' not in _model:
#             model['creator'] = '_deleted'
#         else:
#             model['creator'] = _model['creator']['username']
    
#     return model

# def save_model_to_database(connection, cursor, model):
#     model['sha256'] = model['sha256']
#     model['filename'] = model['filename']
#     model['id'] = model['id'] if model['id'] != None else -1
#     model['version'] = model['version'] if model['version'] != None else -1
#     model['base_model'] = model['base_model'] if model['base_model'] != None else 'null'
#     model['type'] = model['type'] if model['type'] != None else 'null'
#     model['creator'] = model['creator'] if model['creator'] != None else 'null'

#     cursor.execute('INSERT INTO models (sha256, filename, id, version, base_model, type, creator) VALUES (?, ?, ?, ?, ?, ?, ?)', (model['sha256'], model['filename'], model['id'], model['version'], model['base_model'], model['type'], model['creator']))

#     connection.commit()

# new_models = get_new_models()
# connection, cursor = connect_to_database()
# stored_models = get_stored_models_from_database(cursor)

# for index, model in enumerate(new_models):
#     log(f'{index + 1}/{len(new_models)} {model['filename']}')

#     is_exist, model = is_exist_in_database(model, stored_models)

#     if is_exist:
#         log(f'    Already in database.')

#         continue
    
#     model = get_model_info(model)
#     save_model_to_database(connection, cursor, model)

#     log(f'    Added to database.')

# connection.close()
    
# # TODO
# # cursor.execute('SELECT * FROM models')
# # stored_models = cursor.fetchall()

# # for model in stored_models:
# #     log(model)
##
