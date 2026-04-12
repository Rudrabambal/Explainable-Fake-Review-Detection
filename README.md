# Explainable Fake Review Detection (Yelp)

This project implements an **explainable fake review detection system** for Yelp-style reviews:

Review → Text Preprocessing → Feature Extraction (TF-IDF + 12 linguistic features) → Feature Fusion → Logistic Regression → Prediction (Fake / Real) → Explainability (LIME) → Flask Web Interface.

## 1. Setup

1. Create and activate a virtual environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Download a Yelp fake review dataset from Kaggle (e.g. `Yelp Fake Review Dataset`) and place the CSV file under a new `data/` folder, for example:

- `data/yelp_fake_reviews.csv`

4. Note the **text column name** and **label column name** in the CSV (e.g. `text` and `label`).

## 2. Training the model

Configure the input file and column names inside `train_model.py` (paths and column constants), then run:

```bash
python train_model.py
```

This will:

- Preprocess text.
- Compute TF-IDF features.
- Compute 12 linguistic features:
  - review_length
  - avg_word_length
  - exclamation_count
  - capital_ratio
  - sentiment_score
  - adjective_ratio
  - adverb_ratio
  - pronoun_count
  - unique_word_ratio
  - stopword_ratio
  - punctuation_count
  - marketing_word_count
- Train a **Logistic Regression** model.
- Save the trained pipeline under `models/fake_review_model.joblib`.

## 3. Running the Flask app

After training:

```bash
python app.py
```

Then open the printed URL (usually `http://127.0.0.1:5000`) in your browser.  
You can enter a review, get a **Fake / Real** prediction, and see an **explanation via LIME** highlighting important words.

