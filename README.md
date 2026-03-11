# 🏥 MediLens - Medical AI Chatbot

**An intelligent medical assistant for patients and healthcare professionals combining NER, RAG, and OCR for comprehensive medical understanding.**

## 🚀 Quick Start (30 seconds)

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Ollama** (for AI reasoning)

### Windows
```batch
start-medilens.bat
```
All servers start in separate windows!

### macOS/Linux
```bash
bash start-medilens.sh
```

### Manual Start
```bash
# Terminal 1 - Python API
python api.py

# Terminal 2 - Node.js Backend
npm run dev

# Terminal 3 - Frontend
cd my-app && npm run dev
```

Then open: **http://localhost:5173**

---

## 🔧 Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
npm install
cd my-app && npm install
```

### 2. Setup Ollama (Required for AI Reasoning)
```bash
# Run the setup script
setup_ollama.bat

# Or manually:
# 1. Install Ollama from: https://ollama.ai/download
# 2. Start Ollama: ollama serve
# 3. Download a model: ollama pull llama3.2:3b
```

### 3. Local Models
MediLens uses pre-downloaded local models for better performance:
- **NER**: `pubmedbert_ner_model/` (BioBERT for medical entity recognition)
- **Query Rewriting**: `biogpt_model/` (BioGPT for intelligent query processing)
- **RAG Database**: `medilens_rag/` (FAISS index + PubMed articles)

---

## 📋 Features

### 🔍 **Medical Entity Recognition (NER)**
- Extracts diseases, medications, body parts, and biomarkers
- Uses BioBERT (biomedical pre-trained model)
- Confidence scoring for each entity

### 🗂️ **Retrieval-Augmented Generation (RAG)**
- Searches PubMed articles for medical evidence
- FAISS vector database for fast similarity search
- Shows relevance scores and article excerpts

### 📷 **Prescription OCR**
- Upload prescription images
- Automatic text extraction
- Medicine parsing (medication, dosage, frequency, duration)

### 💬 **Natural Language Processing**
- Query rewriting to medical keywords
- Entity grouping and classification
- Support for text and image inputs

### 🎨 **Modern Web UI**
- React/Vite frontend
- Responsive design (mobile-friendly)
- Tab-based results display
- Real-time loading indicators

---

## 🛠️ Requirements

### Hardware
- **GPU**: 4GB+ (tested on GTX 1650)
- **RAM**: 8GB+
- **Storage**: 50GB free space
- **Internet**: For initial model downloads

### Software
- **Python**: 3.8+ ([Download](https://www.python.org/downloads/))
- **Node.js**: 16+ ([Download](https://nodejs.org/))
- **git**: Latest ([Download](https://git-scm.com/))

Verify installation:
```bash
python --version    # Should be 3.8+
node --version     # Should be 16+
npm --version      # Should be 8+
```

---

## 📦 Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd MediLens
```

### 2. Python Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python packages (first time - may take 5-10 mins)
pip install -r requirements.txt
```

### 3. Node.js Setup
```bash
# Install backend dependencies
npm install

# Install frontend dependencies
cd my-app
npm install
cd ..
```

---

## 🎯 Usage

### Option 1: Text Input
1. Open http://localhost:5173
2. Click "📝 Text Input" tab
3. Type your medical question
4. Click "🔍 Analyze"

**Example inputs:**
- "I have severe headache and fever for 2 days, what could be the cause?"
- "What are side effects of Paracetamol 500mg?"
- "Patient diagnosed with Type 2 diabetes, which medicines are prescribed?"

### Option 2: Image Upload
1. Click "📷 Upload Prescription" tab
2. Upload prescription image (JPG/PNG)
3. System extracts text and processes automatically

### View Results
- **Results Tab**: Extracted medicines, keywords
- **Entities Tab**: Grouped medical entities with confidence
- **References Tab**: Relevant PubMed articles, ranked by relevance

---

## 🏗️ Project Structure

```
MediLens/
├── api.py                      # Python Flask API (NER, RAG, ML)
├── server.js                   # Node.js Express backend
├── requirements.txt            # Python dependencies
├── package.json               # Node.js dependencies
│
├── services/
│   ├── nlpService.js         # NLP functions (calls Python API)
│   └── ocrService.js         # OCR using Tesseract.js
│
├── routes/
│   └── prescription.js       # API routes and endpoints
│
├── my-app/                   # React/Vite frontend
│   ├── src/
│   │   ├── App.jsx           # Main app component
│   │   ├── App.css           # App styles
│   │   ├── main.jsx          # Entry point
│   │   └── components/       # React components
│   │       ├── InputForm.jsx
│   │       ├── ResultsDisplay.jsx
│   │       ├── EntityDisplay.jsx
│   │       └── RAGResults.jsx
│   └── package.json
│
├── medilens_rag/             # RAG data
│   ├── pubmed_index.faiss    # FAISS vector index
│   ├── texts.json            # PubMed abstracts
│   └── embeddings.npy        # Pre-computed embeddings
│
├── models/                   # Pre-trained ML models
│   ├── biogpt_model/        # BioGPT (future use)
│   ├── medlens_biobert/     # BioBERT (NER)
│   ├── pubmedbert_ner_model/ # PubMedBERT (alternative NER)
│   └── sarvam-30b/          # Sarvam-30B (future reasoning)
│
├── SETUP_GUIDE.md           # Detailed setup guide
├── HARDWARE_OPTIMIZATION.md # GPU optimization tips
├── README.md                # This file
└── start-medilens.bat       # Quick start script
```

---

## 🔌 API Endpoints

### Python API (Port 5001)
```
POST /api/ai/ner                # Extract medical entities
POST /api/ai/rewrite-query      # Rewrite query to keywords
POST /api/ai/rag-search         # Search PubMed articles
POST /api/ai/process            # Complete pipeline
GET  /api/health                # Health check
POST /api/cleanup               # Clear GPU memory
```

### Node.js Backend (Port 5000)
```
POST /api/upload                # Upload and process prescription
POST /api/query                 # Process text query
POST /api/entities              # Extract entities from text
POST /api/pubmed-search         # Search PubMed
GET  /api/health                # Health check
```

### Example API Call
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I have diabetes and take Metformin 500mg twice daily",
    "includeRag": true
  }'
```

---

## ⚙️ Configuration

### GPU Optimization
The system is pre-configured for 4GB GPU:
- Uses lightweight embeddings model (all-MiniLM-L6-v2)
- Lazy loads models (load only when needed)
- Automatic GPU memory cleanup

**For different GPU sizes:**
- **2GB**: Use CPU mode (`device="cpu"` in api.py)
- **8GB+**: No changes needed (already optimized)

See [HARDWARE_OPTIMIZATION.md](HARDWARE_OPTIMIZATION.md) for advanced tuning.

### Port Configuration
Default ports:
- Python API: 5001
- Node.js: 5000
- Frontend: 5173

To change, edit:
- Python: Line in `api.py` → `port=YOUR_PORT`
- Node.js: Line in `server.js` → `PORT = YOUR_PORT`

---

## 🐛 Troubleshooting

### "CUDA out of memory"
```bash
# Solution 1: Restart Python API
# Solution 2: Clear cache
curl -X POST http://localhost:5001/api/cleanup
# Solution 3: Use CPU mode in api.py
```

### "Python not found"
```bash
# Install Python 3.8+ from https://www.python.org/
# Or if installed, ensure it's on PATH:
where python  # Windows
which python  # macOS/Linux
```

### "Cannot connect to server"
```bash
# Check if servers are running
# Python: Should see "Running on http://0.0.0.0:5001"
# Node: Should see "Server running on port 5000"

# If ports conflict:
# 1. Find process using port:
netstat -anob | findstr :5001  # Windows
lsof -i :5001                  # macOS/Linux

# 2. Kill process and restart
```

### Models Not Loading
```bash
# Clear Hugging Face cache
rm -rf ~/.cache/huggingface/  # macOS/Linux
rmdir /s %USERPROFILE%\.cache\huggingface\  # Windows

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### Frontend Not Connecting
```bash
# Check browser console (F12)
# Ensure Node.js backend running on port 5000
# Try: curl http://localhost:5000/
```

---

## 📊 Performance

### Typical Response Times (4GB GPU)
- **NER Only**: 100-200ms
- **Query Rewrite**: 80-120ms
- **RAG Search**: 200-500ms
- **Full Pipeline**: 600-1000ms
- **OCR Processing**: 2-5 seconds

**CPU Mode**: 5-10x slower but always available

### Memory Usage
- GPU Peak: ~1.2-1.5GB
- System RAM: ~1-2GB
- Safe headroom: ✅ Yes (plenty of buffer in 4GB GPU)

---

## 🔐 Privacy & Security

📌 **Important**: This is an educational tool. Always consult healthcare professionals.

- ✅ All processing happens **locally** on your machine
- ✅ No data sent to external servers (except initial model downloads)
- ✅ Image uploads not stored permanently
- ✅ Queries not logged or tracked

---

## 🚀 Advanced Usage

### Disable RAG for Speed
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your query",
    "includeRag": false
  }'
```

### Get Entity Extraction Only
```bash
curl -X POST http://localhost:5000/api/entities \
  -H "Content-Type: application/json" \
  -d '{"text": "Patient has hypertension"}'
```

### Custom PubMed Search
```bash
curl -X POST http://localhost:5000/api/pubmed-search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "diabetes treatment",
    "topK": 5
  }'
```

---

## 📚 Additional Resources

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed installation & configuration
- **[HARDWARE_OPTIMIZATION.md](HARDWARE_OPTIMIZATION.md)** - GPU optimization tips
- **[Models Documentation](models/)** - Details on included models

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Multi-language support
- Additional medical data sources
- Enhanced UI components
- Performance optimizations
- Better error handling

---

## 📝 License

MIT License - See LICENSE file for details

---

## ⚠️ Disclaimer

**MediLens is an AI-POWERED EDUCATIONAL TOOL ONLY.**

- 🏥 **NOT** a substitute for professional medical advice
- 🏥 **ALWAYS** consult qualified healthcare professionals
- 🏥 Results are generated from AI and may contain errors
- 🏥 Never make medical decisions based solely on this tool

Use responsibly. Your health matters.

---

## 📞 Support

For issues:
1. Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed help
2. Review terminal logs for errors
3. Check browser console (F12) for frontend issues
4. Verify all services running: `http://localhost:5000/` and `http://localhost:5001/api/health`

---

## 🎉 What's New

**v1.0.0** (Initial Release)
- ✅ NER with BioBERT
- ✅ RAG with PubMed (FAISS)
- ✅ OCR for prescriptions
- ✅ Modern React UI
- ✅ 4GB GPU optimization
- ✅ Complete API

**Upcoming**
- 🔜 Conversation history
- 🔜 User authentication
- 🔜 Mobile app
- 🔜 Multi-language support

---

**Made with ❤️ for better healthcare understanding**

**Version**: 1.0.0  
**Last Updated**: March 2026
