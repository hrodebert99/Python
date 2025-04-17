import os

include_paths = [
    '.\\checkpoints',
    '.\\embeddings',
    '.\\loras',
    '.\\vae'
]

exclude_files = [
    '.\\checkpoints\\put_checkpoints_here',
    '.\\embeddings\\put_embeddings_or_textual_inversion_concepts_here',
    '.\\loras\\put_loras_here',
    '.\\vae\\put_vae_here'
]

for root, folders, files in os.walk('.'):
    if not root in include_paths:
        continue
    
    for file in files:
        if f'{root}\\{file}' in exclude_files:
            continue
        
        try:
            os.rename(f'{root}\\{file}', f'.\\{file}')
        except FileExistsError:
            continue
    
    if not os.listdir(root):
        os.rmdir(root)
