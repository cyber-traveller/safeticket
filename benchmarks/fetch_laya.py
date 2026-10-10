"""Download only the two approved Laya checkpoints and verify their hashes."""
import hashlib
from pathlib import Path
from huggingface_hub import snapshot_download

REVISION = '7b928d828b7b0e022f929d9bd2e44165aa270148'
HASHES = {'model.safetensors': '891102d372688fc2a094dac56a384bc537b87c63f21f9f3dac0be2b7cbc8d86c',
          'typed-decisions/model.safetensors': '4fa56de72383a9d3efa9cfa78955733c81b9fc8067a587ca4beb82c78107a24e'}

if __name__ == '__main__':
    root = snapshot_download('convaiinnovations/laya', revision=REVISION,
        local_dir='work/laya-models', allow_patterns=['README.md', 'config.json', 'rl_agent_config.json',
        'model.safetensors', 'encoder/*', 'tokenizer/*', 'typed-decisions/*'], max_workers=2)
    for filename, expected in HASHES.items():
        with (Path(root)/filename).open('rb') as f:
            actual = hashlib.file_digest(f, 'sha256').hexdigest()
        if actual != expected:
            raise RuntimeError('Checksum mismatch: '+filename)
        print('Verified', filename, actual, flush=True)
