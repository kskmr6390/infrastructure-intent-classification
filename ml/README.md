# Machine Learning

This directory contains all ML-related code for intent classification.

## Structure

```
ml/
├── data/                    # Data handling
│   ├── raw/                 # Raw datasets
│   ├── processed/           # Processed data
│   ├── feedback/            # User feedback data
│   ├── data_loader.py       # Data loading utilities
│   ├── self_learning.py     # Self-learning system
│   └── docs/                # Data documentation
├── model/                   # Model storage
│   ├── saved_models/        # Trained models
│   └── docs/                # Model documentation
├── traditional_ml/          # Traditional ML models
│   ├── model.py             # Model definitions
│   ├── train.py             # Training scripts
│   ├── inference.py         # Inference scripts
│   ├── evaluate.py          # Evaluation scripts
│   ├── visualizer.py        # Visualization utilities
│   └── docs/                # Traditional ML docs
└── llm/                     # LLM-based models
    ├── llm_model.py         # LLM model definitions
    ├── train_llm.py         # LLM training scripts
    ├── train_llm_custom.py  # Custom LLM training
    ├── inference_llm.py     # LLM inference
    └── docs/                # LLM documentation
```

## Models

### Traditional ML
- TF-IDF + SVM
- TF-IDF + Random Forest
- Ensemble models

### LLM-based
- Sentence transformers
- Fine-tuned language models
- Hybrid approaches

## Training

### Traditional Models
```bash
cd /path/to/project
python -m ml.traditional_ml.train
```

### LLM Models
```bash
cd /path/to/project
python -m ml.llm.train_llm
```

## Evaluation
```bash
python -m ml.traditional_ml.evaluate
```

## Data

- Raw datasets in `data/raw/`
- Processed features in `data/processed/`
- Feedback data in `data/feedback/`

## Configuration

Model configuration is in `config.yaml` at the project root.

Key parameters:
- `model.type`: Model type to use
- `model.tfidf`: TF-IDF settings
- `model.svm`: SVM settings
- `model.llm`: LLM settings

