import datetime
import sqlite3
import os
import hashlib
import glob

log_filename = f'{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.log'

def log(message):
    message = f'[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}'

    with open(log_filename, 'a', encoding = 'utf-8') as file:
        file.write(f'{message} \n')

    print(message)

def connect_to_database():
    log('Connecting to database...')

    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    return connection, cursor

def close_database(connection):
    log('Closing database connection...')

    connection.close()

def create_tables(connection, cursor):
    log('Creating tables...')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE NOT NULL,
            hash TEXT UNIQUE NOT NULL,
            civitai_model_id INTEGER REFERENCES civitai_models (id) DEFAULT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS base_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS creators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS civitai_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER NOT NULL,
            model_version_id INTEGER UNIQUE NOT NULL,
            type_id INTEGER REFERENCES types (id),
            base_model_id INTEGER REFERENCES base_models (id),
            creator_id INTEGER REFERENCES creators (id) DEFAULT 1,
            CONSTRAINT unique_air UNIQUE (model_id, model_version_id)
        )
    ''')

    connection.commit()

def insert_default_data(connection, cursor):
    log('Inserting default data...')

    cursor.execute('''
        SELECT 1 FROM creators WHERE name = ?
    ''', ('None',))
    row = cursor.fetchone()

    if row != None:
        return
    
    cursor.execute('INSERT INTO creators (name) VALUES  (?)', ('None',))
    
    connection.commit()

def calculate_hash(file_path):
    log(f'Calculating hash for {file_path}...')

    hash = hashlib.sha256()

    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            hash.update(chunk)
    
    return hash.hexdigest()

def insert_model_to_database(connection, cursor, file_path, hash):
    log(f'Inserting {file_path} into database...')

    cursor.execute('INSERT INTO models (file_path, hash) VALUES  (?, ?)',(file_path, hash))
    
    connection.commit()

def process_models(connection, cursor):
    models_folder_path = '.\\models'

    exclude_files = [
        '.\\models\\checkpoints\\put_checkpoints_here',
        '.\\models\\clip\\put_clip_or_text_encoder_models_here',
        '.\\models\\clip_vision\\put_clip_vision_models_here',
        '.\\models\\configs\\anything_v3.yaml',
        '.\\models\\configs\\v1-inference_clip_skip_2_fp16.yaml',
        '.\\models\\configs\\v1-inference_clip_skip_2.yaml',
        '.\\models\\configs\\v1-inference_fp16.yaml',
        '.\\models\\configs\\v1-inference.yaml',
        '.\\models\\configs\\v1-inpainting-inference.yaml',
        '.\\models\\configs\\v2-inference_fp32.yaml',
        '.\\models\\configs\\v2-inference-v_fp32.yaml',
        '.\\models\\configs\\v2-inference-v.yaml',
        '.\\models\\configs\\v2-inference.yaml',
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
        '.\\models\\ipadapter\\ip-adapter_sd15_light.bin',
        '.\\models\\ipadapter\\ip-adapter_sd15.bin',
        '.\\models\\ipadapter\\ip-adapter_sdxl_vit-h.bin',
        '.\\models\\ipadapter\\ip-adapter_sdxl_vit-h.safetensors',
        '.\\models\\ipadapter\\ip-adapter_sdxl.bin',
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
        '.\\models\\vae\\SDXL 1.0\\nucleardiffusion\\sdxl_vae.safetensors',

        '.\\models\\stable_diffusion_model_organizer.py',
        '.\\models\\model_directory_flattener.py'
    ]

    for root, _, files in os.walk(models_folder_path):
        for file in files:
            file_path = f'{root}\\{file}'

            if file_path in exclude_files:
                log(f'{file_path} is in exclusion list. Skipping...')

                continue

            cursor.execute('SELECT * FROM models WHERE file_path = ?', (file_path,))
            row = cursor.fetchone()
            
            if row != None:
                log(f'{file_path} already exist. Skipping...')

                continue

            hash = calculate_hash(file_path)
            
            insert_model_to_database(connection, cursor, file_path, hash)

    model_extensions = [
        '*.safetensors'
    ]

    for extension in model_extensions:
        for model in glob.glob(extension):
            log(model)

if __name__ == '__main__':
    connection, cursor = connect_to_database()
    create_tables(connection, cursor)
    insert_default_data(connection, cursor)
    process_models(connection, cursor)
    close_database(connection)
