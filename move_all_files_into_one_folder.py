import os

include_paths = [
    '.\\models\\checkpoints',
    '.\\models\\embeddings',
    '.\\models\\loras',
    '.\\models\\vae'
]

exclude_files = [
    '.\\models\\checkpoints\\put_checkpoints_here',
    '.\\models\\embeddings\\put_embeddings_or_textual_inversion_concepts_here',
    '.\\models\\loras\\put_loras_here',
    '.\\models\\vae\\put_vae_here'
]

for root, folders, files in os.walk('.'):
    if not root in include_paths:
        continue
    
    for file in files:
        if f'{root}\\{file}' in exclude_files:
            continue
        
        try:
            os.rename(f'{root}\\{file}', f'.\\models\\{file}')
        except FileExistsError:
            continue
    
    if not os.listdir(root):
        os.rmdir(root)
