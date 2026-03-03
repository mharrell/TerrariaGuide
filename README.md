# TerrariaGuide 🗡️

A fine-tuned large language model trained on the Terraria wiki, capable of answering questions about items, crafting, bosses, enemies, biomes, and game mechanics.

## Overview

TerrariaGuide is a domain-specific LLM fine-tune built by scraping, cleaning, and processing the entire Terraria wiki into structured training data, then fine-tuning a base Llama model using LoRA via Unsloth.

## Pipeline

### 1. Data Collection (`scraper.py`)
- Scrapes the Terraria wiki (terraria.wiki.gg) using the MediaWiki API
- Collects **3,375 pages** of game content
- Stores raw wiki markup as structured JSON

### 2. Data Cleaning (`data_cleaner.py`)
- Strips wiki markup, templates, and image references
- Extracts useful content from templates (coin values, crafting info, version notes, durations)
- Converts `{{coin|...}}` templates to readable gold/silver/copper values
- Filters out redirect pages, gallery sections, and non-English subpages
- Outputs **2,399 cleaned pages**

### 3. Training Pair Generation (`pair_generator.py`)
- Generates instruction/response pairs for each wiki section
- Maps section headings (tips, history, drops, crafting, etc.) to relevant questions
- Includes boss spawn message recognition pairs
- Generates **~22,000 base training pairs**

### 4. Crafting Data Recovery (`crafting_recovery.py`)
- Supplements crafting data using the Terraria wiki Cargo API
- Recovers ingredient amounts lost during wiki markup cleaning
- Adds **~10,000 crafting-specific pairs**

### 5. Training (`train.py`)
- Fine-tunes using [Unsloth](https://github.com/unslothai/unsloth) for 2x speed improvement
- LoRA fine-tuning (r=8, alpha=16) on a Llama 3.1 8B base model
- 4-bit quantization for consumer GPU compatibility
- Trained on **32,923 total pairs** for 1 epoch

## Stats

| Metric | Value |
|--------|-------|
| Raw pages scraped | 3,375 |
| Cleaned pages | 2,399 |
| Total training pairs | 32,923 |
| Base model | Llama 3.1 8B Instruct |
| Trainable parameters | ~0.75% (LoRA) |
| Training hardware | NVIDIA RTX 3060 Ti (8GB) |
| Final training loss | 0.9464 |

## Usage

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="models/terraria-guide",
    max_seq_length=512,
    load_in_4bit=True,
)
FastLanguageModel.for_inference(model)
```

Or use the interactive inference script:

```
python inference.py
```

## Requirements

- Python 3.12
- NVIDIA GPU with 8GB+ VRAM
- CUDA 12.1
- See `requirements.txt` for full dependencies

## Project Structure

```
TerrariaGuide/
├── data/
│   ├── raw/                  # Scraped wiki data
│   ├── cleaned/              # Cleaned wiki data
│   └── training/             # Training pairs (JSONL)
├── models/
│   └── terraria-guide/       # Fine-tuned model weights
├── scraper.py
├── data_cleaner.py
├── pair_generator.py
├── crafting_recovery.py
├── train.py
├── inference.py
└── run_pipeline.py           # Runs full data pipeline
```

## Acknowledgements

- [Terraria Wiki](https://terraria.wiki.gg) for the game data
- [Unsloth](https://github.com/unslothai/unsloth) for the fast fine-tuning framework
- [Re-Logic](https://re-logic.com) for creating Terraria