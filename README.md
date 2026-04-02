# 🔍 ReviewRefinery: Explainable Fake Review Detection

[![NLP](https://img.shields.io/badge/NLP-Natural%20Language%20Processing-blueviolet)](https://en.wikipedia.org/wiki/Natural_language_processing)
[![Machine Learning](https://img.shields.io/badge/ML-Machine%20Learning-blue)](https://en.wikipedia.org/wiki/Machine_learning)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask-lightgrey)](https://flask.palletsprojects.com/)

**ReviewRefinery** is a state-of-the-art Natural Language Processing (NLP) system designed to detect deceptive or "fake" reviews. Unlike "black-box" models, ReviewRefinery provides detailed emotional analysis and word-level explainability, empowering users to understand *why* a review was flagged.

---

## 🛠️ Key Features

- **🎯 High-Accuracy Detection**: Hybrid model combining TF-IDF vectorization with 12 handcrafted linguistic features.
- **🧠 Transparent Explainability**: Leverages **SHAP (SHapley Additive exPlanations)** to highlight influential words in real-time.
- **🎭 Multi-Dimensional NLP**:
  - **Sentiment Analysis**: Detects the underlying polarity (Positive/Negative/Neutral).
  - **Emotion Detection**: Identifies 8 core emotions (Joy, Anger, Trust, etc.) using the NRC Lexicon.
- **📊 Intelligence Dashboard**: A premium, modern React interface with glassmorphism aesthetics.
- **⚠️ Heuristic Categorization**: Specifically flags reviews as "Promotional", "Spam", or "Authentic" based on keyword density and AI confidence.

---

## 🔬 NLP & Machine Learning Deep Dive

### 1. The Linguistic Engine
The core model doesn't just look at words—it analyzes the **DNA of the writing style**. We extract 12 specific linguistic features:
- **Style Metrics**: Capitalization ratio, punctuation density, and exclamation counts (often higher in deceptive reviews).
- **Complexity**: Average word length and total token count.
- **Lexical Richness**: Unique word ratio and stopword distribution.
- **Socio-Linguistic Cues**: Adjective/Adverb ratios and personal pronoun frequency.

### 2. The Hybrid Pipeline
We use a `ColumnTransformer` to fuse two powerful feature sets:
1. **TF-IDF (Term Frequency-Inverse Document Frequency)**: Captures the importance of specific words and bigrams.
2. **Linguistic Features**: Captures the structural patterns of deception.

These are fed into a **Balanced Logistic Regression** model, optimized for handling skewed datasets.

### 3. Explainability with SHAP
We integrate **SHAP** to provide local explanations. For every prediction, the system calculates the "Shapley Value" for each token, visualizing:
- 🔴 **Red Highlights**: Words that pushed the model toward a "Fake" prediction.
- 🔵 **Blue Highlights**: Words that suggest the review is "Real".

---

## 💻 Tech Stack

- **Backend**: Python, Flask, Joblib.
- **AI/ML**: Scikit-Learn, Pandas, NumPy.
- **NLP**: NLTK, TextBlob, NRCLex.
- **Explainability**: SHAP.
- **Frontend**: React, Vite, CSS3 (Modular Styles).

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js (for frontend)

### 1. Backend Setup
```bash
# Navigate to the project root
cd "NLP project"

# Install dependencies
pip install -r requirements.txt

# Train the model (ensure data is in archive/ folder)
python train_model.py

# Start the Flask API
python app.py
```

### 2. Frontend Setup
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

---

## 📂 Project Structure

```text
NLP project/
├── app.py                # Flask API & SHAP integration
├── train_model.py        # ML Training Pipeline
├── features.py           # Custom Linguistic Feature Extractor
├── models/               # Sub-directory for saved .joblib models
├── archive/              # Dataset storage (Yelp)
└── frontend/             # React application source
```

---

## 📄 License
This project is for educational and research purposes in the field of Explainable AI (XAI) and NLP.

