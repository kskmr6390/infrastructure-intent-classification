#!/bin/bash
# Verify all necessary files are present for Heroku deployment

echo "=== Verifying Heroku Deployment Files ==="
echo ""

# Check models
echo "✓ Checking Traditional ML Models..."
if ls ml/model/saved_models/tfidf_svm_model_*.pkl 1> /dev/null 2>&1; then
    echo "  Found: $(ls ml/model/saved_models/tfidf_svm_model_*.pkl | wc -l) TF-IDF models"
else
    echo "  ✗ ERROR: No TF-IDF models found!"
    exit 1
fi

if ls ml/model/saved_models/intent_mapping_*.pkl 1> /dev/null 2>&1; then
    echo "  Found: $(ls ml/model/saved_models/intent_mapping_*.pkl | wc -l) intent mappings"
else
    echo "  ✗ ERROR: No intent mappings found!"
    exit 1
fi

# Check dataset
echo ""
echo "✓ Checking Dataset..."
if [ -f ml/data/raw/infra_copilot_intent_dataset_v2.jsonl ]; then
    echo "  Found: ml/data/raw/infra_copilot_intent_dataset_v2.jsonl"
else
    echo "  ✗ ERROR: Dataset v2 not found!"
    exit 1
fi

# Check frontend
echo ""
echo "✓ Checking Frontend..."
if [ -f frontend/templates/chat.html ]; then
    echo "  Found: frontend/templates/chat.html"
else
    echo "  ✗ ERROR: chat.html not found!"
    exit 1
fi

if [ -f frontend/static/js/app.js ]; then
    echo "  Found: frontend/static/js/app.js"
else
    echo "  ✗ ERROR: app.js not found!"
    exit 1
fi

# Check guides
echo ""
echo "✓ Checking Guides..."
if [ -d guides ]; then
    echo "  Found: guides/ directory with $(ls guides/*.md 2>/dev/null | wc -l) files"
else
    echo "  ✗ ERROR: guides/ directory not found!"
    exit 1
fi

# Check config
echo ""
echo "✓ Checking Config..."
if [ -f config.yaml ]; then
    echo "  Found: config.yaml"
else
    echo "  ✗ ERROR: config.yaml not found!"
    exit 1
fi

# Check backend
echo ""
echo "✓ Checking Backend..."
if [ -f backend/main.py ]; then
    echo "  Found: backend/main.py"
else
    echo "  ✗ ERROR: backend/main.py not found!"
    exit 1
fi

# Check requirements
echo ""
echo "✓ Checking Requirements..."
if [ -f requirements.txt ]; then
    echo "  Found: requirements.txt"
    if grep -q "torch" requirements.txt; then
        echo "  ⚠️  WARNING: PyTorch still in requirements.txt!"
    else
        echo "  ✓ PyTorch removed (good for slug size)"
    fi
else
    echo "  ✗ ERROR: requirements.txt not found!"
    exit 1
fi

# Check Procfile
echo ""
echo "✓ Checking Procfile..."
if [ -f Procfile ]; then
    echo "  Found: Procfile"
    cat Procfile
else
    echo "  ✗ ERROR: Procfile not found!"
    exit 1
fi

# Check git status
echo ""
echo "✓ Checking Git Status..."
echo "  Files in git:"
echo "    Models: $(git ls-files ml/model/saved_models/*.pkl | wc -l) files"
echo "    Dataset: $(git ls-files ml/data/raw/*.jsonl | wc -l) files"
echo "    Frontend: $(git ls-files frontend/ | wc -l) files"
echo "    Guides: $(git ls-files guides/ | wc -l) files"

echo ""
echo "=== All Checks Passed! ==="
echo ""
echo "Ready to deploy with:"
echo "  git push heroku main"

