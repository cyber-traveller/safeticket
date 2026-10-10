"""Train a small independent SafeTicket support adapter with LoRA.

This is a prototype training run, not a claim of production quality.
"""
import json
import os
from pathlib import Path

import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(os.environ.get(
    'SAFETICKET_BASE_MODEL',
    str(ROOT / 'work' / 'alternatives' / 'open-alternative-jev' / 'models' / 'qwen2.5-0.5b-instruct'),
))
DATA = [Path(item) for item in os.environ.get(
    'SAFETICKET_TRAIN_DATA',
    str(ROOT / 'work' / 'safeticket-independent' / 'data' / 'train.jsonl'),
).split(',')]
OUT = Path(os.environ.get(
    'SAFETICKET_ADAPTER_OUT',
    str(ROOT / 'work' / 'safeticket-independent' / 'adapters' / 'qwen2.5-0.5b-support-v0.1'),
))


class Rows(torch.utils.data.Dataset):
    def __init__(self, rows, tokenizer):
        self.items = []
        for row in rows:
            prompt = tokenizer.apply_chat_template(row['messages'][:-1], tokenize=False, add_generation_prompt=True)
            prompt_ids = tokenizer(prompt, add_special_tokens=False)['input_ids']
            answer_ids = tokenizer(row['messages'][-1]['content'] + tokenizer.eos_token, add_special_tokens=False)['input_ids']
            input_ids = (prompt_ids + answer_ids)[:256]
            encoded = {'input_ids': input_ids, 'attention_mask': [1] * len(input_ids)}
            encoded['labels'] = ([-100] * len(prompt_ids) + answer_ids)[:256]
            self.items.append(encoded)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return self.items[index]


class Collator:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def __call__(self, features):
        batch = self.tokenizer.pad(features, return_tensors='pt')
        batch['labels'][batch['attention_mask'] == 0] = -100
        return batch


def main():
    tokenizer = AutoTokenizer.from_pretrained(BASE)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(BASE, torch_dtype=torch.float32)
    model.config.use_cache = False
    model = get_peft_model(model, LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05,
        target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'],
        task_type='CAUSAL_LM',
    ))
    model.print_trainable_parameters()
    rows = [json.loads(line) for data_path in DATA for line in data_path.read_text().splitlines() if line.strip()]
    args = TrainingArguments(
        output_dir=str(OUT),
        num_train_epochs=float(os.environ.get('SAFETICKET_EPOCHS', '3')),
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        learning_rate=float(os.environ.get('SAFETICKET_LR', '5e-4')),
        logging_steps=5,
        save_strategy='no',
        report_to=[],
        remove_unused_columns=False,
        use_cpu=True,
    )
    trainer = Trainer(model=model, args=args, train_dataset=Rows(rows, tokenizer), data_collator=Collator(tokenizer))
    trainer.train()
    model.save_pretrained(OUT)
    tokenizer.save_pretrained(OUT)
    (OUT / 'TRAINING_NOTES.json').write_text(json.dumps({
        'base_model_path': str(BASE),
        'base_model_license': 'Apache-2.0',
        'dataset': str(DATA),
        'examples': len(rows),
        'method': 'LoRA causal-language fine-tuning; CPU prototype',
        'not_production_ready': True,
    }, indent=2) + '\n')
    print(json.dumps({'output': str(OUT), 'examples': len(rows)}, indent=2))


if __name__ == '__main__':
    main()
