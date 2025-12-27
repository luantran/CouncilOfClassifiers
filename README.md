# Council of Classifiers: CEFR Ensemble Text Classifier

[![Python 3.12+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/react-18.3-blue.svg)](https://reactjs.org/)
[![HuggingFace](https://img.shields.io/badge/🤗-models-yellow)](https://huggingface.co/collections/theluantran/cefr-classifiers-one-model-to-grade-them-all)

A production-ready ensemble system for classifying English text by CEFR proficiency levels (A1, A2, B1, B2, C1/C2). The "Council of Classifiers" combines three distinct machine learning approaches to provide robust, accurate predictions through consensus.

## Key Features

- **Three-Model Ensemble**: Combines Naive Bayes, Doc2Vec, and fine-tuned BERT for robust predictions
- **Dual Prediction Methods**: Majority voting and mean probability aggregation
- **Modern Web Interface**: React + Vite frontend with real-time classification
- **REST API**: JSON endpoints for programmatic access
- **Production Ready**: Deployed on Render with models hosted on HuggingFace Hub

### Installation

```bash
# Clone the repository
git clone https://github.com/luantran/CouncilOfClassifiers.git
cd CouncilOfClassifiers

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies (for development)
cd frontend
npm install
cd ..
```

### Running the Application

#### Development Mode (Frontend + Backend)

```bash
# Terminal 1: Start Flask backend
python run.py

# Terminal 2: Start Vite dev server
cd frontend
npm run dev
```

Access the application at `http://localhost:5173`

#### Production Mode (Unified Flask App)

```bash
# Build frontend
cd frontend
npm run build
cd ..

# Set environment to production
export FLASK_ENV=production

# Run Flask app (serves both API and built React frontend)
python run.py
```

Access at `http://localhost:5000`

## API Usage

### Predict Endpoint

```bash
POST /api/predict
Content-Type: application/json

{
  "text": "This is a sample text to classify by CEFR level."
}
```

**Response:**

```json
{
  "text": "This is a sample text to classify by CEFR level.",
  "predictions": {
    "Naive Bayes": 2,
    "Doc2Vec": 2,
    "BERT": 3
  },
  "probabilities": {
    "Naive Bayes": [0.05, 0.10, 0.65, 0.15, 0.05],
    "Doc2Vec": [0.03, 0.08, 0.72, 0.12, 0.05],
    "BERT": [0.02, 0.07, 0.45, 0.38, 0.08]
  },
  "majority_vote": 2,
  "mean_probabilities": [0.033, 0.083, 0.606, 0.216, 0.06],
  "mean_pred": 2,
  "mean_pred_proba": 0.606,
  "use_majority_vote": true,
  "confidence": 0.67,
  "stats": {
    "num_models": 3,
    "agreement_count": 2,
    "all_agree": false
  }
}
```

**CEFR Level Mapping:**
- `0` = A1 (Beginner)
- `1` = A2 (Elementary)
- `2` = B1 (Intermediate)
- `3` = B2 (Upper Intermediate)
- `4` = C1/C2 (Advanced/Proficient)

## Model Details

**Models**: [HuggingFace Profile](https://huggingface.co/collections/theluantran/cefr-classifiers-one-model-to-grade-them-all)

**Model Source Code**: [Github Repo](https://github.com/luantran/One-model-to-grade-them-all)  

*Note: Training data is proprietary and not included in this repository.*