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
    '.\\models\\vae_approx\\taesdxl_encoder.pth'
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

cursor.execute('SELECT * FROM models')
models_in_database = cursor.fetchall()

for index, model in enumerate(models_in_database):
    models_in_database[index] = dict(zip([description[0] for description in cursor.description], model))

for root, folders, files in os.walk('.\\models'):
    for filename in files:
        log(f'Processing {filename}...')

        file_path = f'{root}\\{filename}'

        if file_path in exclude_files:
            log(f'    Excluded.')

            continue

        if file_path in [model['file_path'] for model in models_in_database]:
            log(f'    Already in database.')

            continue

        hasher = hashlib.sha256()

        with open(file_path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b''):
                hasher.update(chunk)
        
        hash = hasher.hexdigest()

        if hash in [model['hash'] for model in models_in_database]:
            log(f'    Already in database.')

            continue

        cursor.execute('INSERT INTO models (hash, filename, file_path) VALUES (?, ?, ?)', (hash, filename, file_path))

        connection.commit()

        log(f'    Added to database.')

cursor.execute('SELECT * FROM models')
models_in_database = cursor.fetchall()

for index, model in enumerate(models_in_database):
    models_in_database[index] = dict(zip([description[0] for description in cursor.description], model))

for model in models_in_database:
    # time.sleep(1)

    log(f'Processing {model['filename']}...')
    log(f'    https://civitai.com/api/v1/model-versions/by-hash/{model['hash']}')

    # response = requests.get(f'https://civitai.com/api/v1/model-versions/by-hash/{model['hash']}')

    # TODO: Response code can be other than 200 or 404. If it is, raise an exception.

    # if response.status_code == 404:
    #     continue
