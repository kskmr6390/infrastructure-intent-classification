#!/bin/bash
# Script to train models

echo "=================================="
echo "Model Training"
echo "=================================="
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found! Run ./start.sh first."
    exit 1
fi

echo "Select model type to train:"
echo "1. Traditional ML (TF-IDF + SVM) - Fast, Good Accuracy"
echo "2. LLM (Sentence Transformers) - Better Accuracy"
echo "3. Both"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo "Training Traditional ML model..."
        python -m ml.traditional_ml.train
        ;;
    2)
        echo "Training LLM model..."
        python -m ml.llm.train_llm
        ;;
    3)
        echo "Training Traditional ML model..."
        python -m ml.traditional_ml.train
        echo ""
        echo "Training LLM model..."
        python -m ml.llm.train_llm
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

echo ""
echo "Training complete!"
echo "Start the server with: ./start.sh"

