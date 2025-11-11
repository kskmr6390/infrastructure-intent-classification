# 🔍 LangSmith Observability Guide

## Overview

LangSmith provides powerful observability and monitoring for your Intent Classification System, allowing you to:

- 📊 **Track all predictions** in real-time
- 🐛 **Debug model performance** issues
- 📈 **Analyze confidence scores** and trends
- 👍 **Monitor user feedback** and corrections
- 🔄 **Identify improvement opportunities**

---

## 🚀 Quick Start

### 1. Sign Up for LangSmith

1. Go to https://smith.langchain.com/
2. Create a free account
3. Get your API key from the settings

### 2. Configure Your Project

Create a `.env` file in the project root:

```bash
# Copy the example
cp .env.example .env
```

Edit `.env` and add your API key:

```bash
# LangSmith Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_actual_api_key_here
LANGCHAIN_PROJECT=intent-classification
```

### 3. Enable LangSmith in Config

Edit `config.yaml`:

```yaml
observability:
  langsmith:
    enabled: true                            # Set to true
    project_name: "intent-classification"    
    tracing_v2: true                        
    endpoint: "https://api.smith.langchain.com"
    log_predictions: true                   
    log_feedback: true                       
    sample_rate: 1.0                         # 1.0 = log everything
```

### 4. Install Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Restart the Server

```bash
./start.sh
```

You should see:
```
✅ LangSmith tracing enabled for project: intent-classification
   View traces at: https://smith.langchain.com/
```

---

## 📊 What Gets Tracked

### Predictions
Every prediction made by the system is automatically logged with:

- **Input Query**: The user's question
- **Predicted Intent**: Model's classification
- **Confidence Score**: Prediction confidence (0-1)
- **All Top Predictions**: Top-K predictions with scores
- **Metadata**:
  - Predictor type (LLM, Traditional, etc.)
  - Model type (TF-IDF+SVM, etc.)
  - Uncertainty flag
  - Timestamp

### User Feedback
When users provide corrections:

- **Original Prediction**: What the model predicted
- **Correct Intent**: What it should have been
- **Confidence Score**: How confident the model was
- **Feedback Metadata**:
  - Message ID
  - Session ID
  - Feedback ID

---

## 🎯 Using LangSmith Dashboard

### Viewing Traces

1. Go to https://smith.langchain.com/
2. Select your project: `intent-classification`
3. View all traces in real-time

### Analyzing Performance

**Filter by Confidence:**
```
Filter traces where confidence < 0.7
```

**Search Specific Intents:**
```
Search for: predicted_intent="interface_status"
```

**View Error Patterns:**
```
Filter by status: ERROR
```

### Creating Datasets

1. **Collect Low-Confidence Predictions**
   - Filter traces with confidence < 0.7
   - Export to dataset for review

2. **Build Test Sets**
   - Select representative samples
   - Create test datasets for evaluation

3. **Track Improvements**
   - Compare before/after retraining
   - Measure accuracy improvements

---

## 📈 Key Metrics to Monitor

### Confidence Distribution
```
Average Confidence: Should be > 0.80
Low Confidence (<0.7): Should be < 20%
```

### Accuracy (from feedback)
```
Correct Predictions / Total Predictions
Target: > 90%
```

### Most Confused Intents
```
Look for patterns where:
- predicted_intent != correct_intent
- confidence was high but wrong
```

### Response Times
```
Track inference latency
Target: < 500ms per prediction
```

---

## 🔧 Configuration Options

### Sample Rate

Control what percentage of predictions to log:

```yaml
observability:
  langsmith:
    sample_rate: 1.0    # Log everything (100%)
    # sample_rate: 0.1  # Log 10% (for high traffic)
    # sample_rate: 0.5  # Log 50%
```

### Selective Logging

Log only predictions or only feedback:

```yaml
observability:
  langsmith:
    log_predictions: true   # Log all predictions
    log_feedback: false     # Don't log feedback
```

### Project Organization

Use different projects for environments:

```yaml
# Development
LANGCHAIN_PROJECT=intent-classification-dev

# Staging
LANGCHAIN_PROJECT=intent-classification-staging

# Production
LANGCHAIN_PROJECT=intent-classification-prod
```

---

## 💡 Best Practices

### 1. **Start with Full Logging**
During initial deployment, log everything (sample_rate: 1.0) to understand behavior

### 2. **Monitor These Metrics**
- Average confidence score
- Low confidence prediction rate
- Feedback correction rate
- Most frequently corrected intents

### 3. **Set Up Alerts**
Configure alerts for:
- Confidence drops below threshold
- Error rate increases
- Specific intents showing poor performance

### 4. **Regular Reviews**
- Weekly: Review top confused intents
- Monthly: Analyze trends and improvements
- After updates: Compare performance before/after

### 5. **Use for Retraining**
- Export low-confidence predictions
- Review user corrections
- Build targeted training datasets

---

## 🐛 Troubleshooting

### LangSmith Not Logging

**Check API Key:**
```bash
echo $LANGCHAIN_API_KEY
# Should show your API key
```

**Check Configuration:**
```bash
# Verify enabled in config.yaml
grep -A5 "observability:" config.yaml
```

**Check Logs:**
```bash
tail -f logs/intent_classification.log | grep -i langsmith
```

### Common Issues

**Issue:** "LangSmith API key not set"
```bash
# Solution: Add key to .env
echo "LANGCHAIN_API_KEY=your_key_here" >> .env
```

**Issue:** "LangSmith package not installed"
```bash
# Solution: Install dependencies
pip install langsmith langchain
```

**Issue:** "No traces appearing"
```bash
# Check if tracing is enabled
echo $LANGCHAIN_TRACING_V2
# Should output: true

# Restart server
pkill -f "python -m backend.main"
./start.sh
```

---

## 📚 Advanced Usage

### Custom Metadata

Predictions automatically include metadata:

```python
{
    'predictor_type': 'llm',
    'model_type': 'tfidf_svm',
    'is_uncertain': False,
    'session_id': 'abc-123',
    'user_id': 'optional'
}
```

### Performance Tracking

The system automatically tracks:
- Prediction latency
- Model load time
- API response time

### Integration with Monitoring

Combine with other tools:
- **Prometheus**: For system metrics
- **Grafana**: For visualization
- **LangSmith**: For ML-specific insights

---

## 📊 Sample Queries

### Find Low Confidence Predictions
```
confidence < 0.7 AND is_uncertain = true
```

### View Specific Intent Performance
```
predicted_intent = "interface_status"
ORDER BY confidence DESC
```

### Identify Correction Patterns
```
predicted_intent != correct_intent
GROUP BY predicted_intent, correct_intent
```

### Monitor Recent Performance
```
timestamp > now() - 24h
AVERAGE(confidence)
```

---

## 🎓 Resources

- **LangSmith Docs**: https://docs.smith.langchain.com/
- **API Reference**: https://api.smith.langchain.com/docs
- **Community**: https://discord.gg/langchain

---

## 🔒 Privacy & Security

### Data Logged
- Query text (user inputs)
- Predictions and confidence scores
- Feedback data
- Metadata (timestamps, IDs, etc.)

### Recommendations
1. **Don't log sensitive data** in production queries
2. **Use sample_rate < 1.0** for PII-sensitive environments
3. **Review LangSmith's privacy policy**
4. **Consider self-hosted alternatives** if needed

---

## ✅ Checklist

- [ ] Signed up for LangSmith account
- [ ] Got API key
- [ ] Added API key to `.env`
- [ ] Enabled in `config.yaml`
- [ ] Installed dependencies
- [ ] Restarted server
- [ ] Verified traces appearing in dashboard
- [ ] Set up project organization
- [ ] Configured sample rate
- [ ] Set up monitoring alerts

---

**Ready to gain insights!** 🚀

View your traces at: https://smith.langchain.com/


