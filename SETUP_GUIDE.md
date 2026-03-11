# 🏥 MediLens - Medical AI Chatbot Setup Guide

## Project Overview

MediLens is a medical intelligence chatbot designed for patients and nurses to understand medical treatments through an AI-powered pipeline:

1. **User Input** → Text or Prescription Image
2. **NER (Named Entity Recognition)** → Extract medical entities using BioBERT
3. **Query Rewriting** → Convert to medical keywords
4. **RAG (Retrieval-Augmented Generation)** → Search PubMed for references
5. **Output** → Structured medical information with references

## Hardware Optimization

**Your Setup:**
- GPU: GTX 1650 (4GB VRAM)
- RAM: 8GB

**Optimizations Applied:**
- ✅ Lightweight models (all-MiniLM for embeddings)
- ✅ Model quantization ready (INT8 support)
- ✅ Lazy model loading (load only when needed)
- ✅ GPU memory management (clear cache after operations)
- ✅ Efficient batch processing
- ✅ No large LLMs loaded (uses BioBERT instead of BioGPT-Large)

## Project Structure

```
MediLens/
├── api.py                 # Python ML API (Flask)
├── server.js             # Node.js backend server
├── requirements.txt      # Python dependencies
├── package.json          # Node.js dependencies
│
├── services/
│   ├── ocrService.js    # OCR using Tesseract
│   └── nlpService.js    # NLP interface to Python API
│
├── routes/
│   └── prescription.js   # API endpoints
│
├── my-app/              # React frontend (Vite)
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/  # UI components
│   │   └── App.css
│   └── package.json
│
├── medilens_rag/        # RAG data
│   ├── pubmed_index.faiss    # Vector database
│   ├── texts.json             # PubMed abstracts
│   └── embeddings.npy        # Pre-computed embeddings
│
└── models/              # Pre-trained models
    ├── biogpt_model/
    ├── medlens_biobert/
    └── pubmedbert_ner_model/
```

## Installation Instructions

### Step 1: Clone & Setup

```bash
cd MediLens
```

### Step 2: Python Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Node.js Setup

```bash
# For main backend
npm install

# For frontend
cd my-app
npm install
cd ..
```

## Running the Application

### Option A: Run Both Servers Manually

**Terminal 1 - Start Python API:**
```bash
python api.py
```

**Terminal 2 - Start Node.js Backend:**
```bash
npm run dev
```

**Terminal 3 - Start React Frontend:**
```bash
cd my-app
npm run dev
```

Then open: `http://localhost:5173` (or the URL shown by Vite)

### Option B: Run Together (if concurrently installed)

```bash
npm run dev:full
```

## Backend Architecture

### Python API (api.py) - Port 5001
- **Lightweight**: Optimized for 4GB GPU
- **Lazy Loading**: Models load on first use
- **Memory Management**: GPU cache clearing after operations
- **Endpoints:**
  - `POST /api/ai/ner` - Extract medical entities
  - `POST /api/ai/rewrite-query` - Query optimization
  - `POST /api/ai/rag-search` - Search PubMed
  - `POST /api/ai/process` - Full pipeline
  - `GET /api/health` - Health check

### Node.js Backend (server.js) - Port 5000
- **API Gateway**: Routes to Python API
- **File Upload**: Handles prescription images
- **OCR**: Uses Tesseract.js
- **Endpoints:**
  - `POST /api/upload` - Upload & process prescription
  - `POST /api/query` - Process text query
  - `POST /api/entities` - Extract entities only
  - `POST /api/pubmed-search` - Search PubMed only

### Frontend (React/Vite)
- **Input Forms**: Text and image upload
- **Tab Interface**: Results, Entities, References
- **Real-time Processing**: Loading indicators
- **Responsive Design**: Mobile-friendly UI

## API Usage Examples

### Example 1: Process Medical Query

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I have severe headache and fever for 2 days",
    "includeRag": true
  }'
```

### Example 2: Upload Prescription Image

```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@prescription.jpg"
```

### Example 3: Extract Entities

```bash
curl -X POST http://localhost:5000/api/entities \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Patient has diabetes and hypertension. Prescribed Metformin 500mg"
  }'
```

## Performance Tips for 4GB GPU

### 1. **Batch Processing**
- Process one query at a time
- Avoid concurrent requests initially

### 2. **Clear Memory**
- API automatically clears GPU cache
- Manually call: `POST /api/cleanup`

### 3. **Model Optimization**
If you hit memory limits:

**Option A - Disable RAG:**
```json
{
  "text": "...",
  "include_rag": false
}
```

**Option B - Reduce Top-K Results:**
```json
{
  "query": "...",
  "top_k": 2
}
```

**Option C - Quantize Models** (advanced)
- Add `bitsandbytes` to requirements
- Use INT8 quantization in api.py

### 4. **Clear Cache Regularly**
```bash
# Call every 10-15 queries
curl -X POST http://localhost:5001/api/cleanup
```

## Troubleshooting

### Error: "CUDA out of memory"
```bash
# Solution 1: Restart Python API
# Solution 2: Reduce batch size in api.py
# Solution 3: Use CPU-only mode (slower)
```

### Error: "Module not found"
```bash
# Install missing packages
pip install -r requirements.txt --force-reinstall
```

### Error: "Connection refused"
- Ensure Python API running on 5001
- Ensure Node.js running on 5000
- Check firewall settings

### Port Already in Use
```bash
# Change port in code:
# Python: Line "port=5001" in api.py
# Node: Line "PORT = 5000" in server.js
```

## Frontend Features

### Input Options
1. **Text Input**: Type or paste medical questions
2. **Image Upload**: Upload prescription images for OCR

### Result Tabs
1. **Results Tab**: Original text, medicines, keywords
2. **Entities Tab**: Grouped medical entities with confidence
3. **References Tab**: PubMed articles with relevance scores

### Processing Indicators
- Loading spinner during processing
- Error messages with retry option
- Character counter for text input
- Confidence/relevance scores for results

## Next Steps & Enhancements

### Phase 1 (Current)
- ✅ NER with BioBERT
- ✅ RAG with PubMed data
- ✅ Basic frontend UI
- ✅ API integration

### Phase 2 (Optional)
- Add LLM reasoning (Ollama/Sarvam locally)
- Persistent chat history
- User authentication
- Database integration

### Phase 3 (Optional)
- Add more medical data sources
- Fine-tune models on medical data
- Add multi-language support
- Mobile app

## Important Notes

⚠️ **Disclaimer**: This is an AI assistant tool for educational and informational purposes only. It should NOT replace professional medical advice. Always consult with healthcare professionals.

🔒 **Privacy**: All processing happens locally. No data sent to external servers (except PubMed search).

😊 **Support**: For issues, check:
1. Console logs in browser (F12)
2. Terminal output from servers
3. ensure all requirements installed

## License
MIT - Feel free to modify and use

---

**Version**: 1.0.0  
**Last Updated**: March 2026  
**MediLens Team**
