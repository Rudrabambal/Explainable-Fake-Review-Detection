import os
from typing import Tuple

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from features import LinguisticFeatureExtractor
from preprocessing import ensure_nltk_data, simple_preprocess


# ---- CONFIGURE THESE FOR YOUR DATASET ----
# Using your Yelp train file in the archive folder:
DATA_PATH = "archive/new_data_train.csv"
# In this file, the review text is in the 'reviewContent' column
TEXT_COLUMN = "reviewContent"
# The fake/real indicator is in the 'flagged' column (1 = fake, 0 = real)
LABEL_COLUMN = "flagged"
TEST_SIZE = 0.2
RANDOM_STATE = 42
MODEL_PATH = "models/fake_review_model.joblib"
# ------------------------------------------


def load_data(path: str) -> Tuple[pd.Series, pd.Series]:
    # Your Yelp file is tab-separated and has a few messy lines; read accordingly.
    df = pd.read_csv(path, sep="\t", engine="python", on_bad_lines="skip")
    if TEXT_COLUMN not in df.columns or LABEL_COLUMN not in df.columns:
        raise ValueError(
            f"Expected columns '{TEXT_COLUMN}' and '{LABEL_COLUMN}' in CSV. "
            f"Found: {list(df.columns)}"
        )
    texts = df[TEXT_COLUMN].astype(str)
    labels = df[LABEL_COLUMN]
    return texts, labels


def build_pipeline() -> Pipeline:
    # Text branch: TF-IDF over preprocessed text
    text_vectorizer = TfidfVectorizer(
        preprocessor=simple_preprocess,
        ngram_range=(1, 2),
        max_features=20000,
    )

    # Linguistic features: custom transformer
    linguistic_extractor = LinguisticFeatureExtractor()

    # ColumnTransformer expects a 2D input; we wrap the single text column
    features = ColumnTransformer(
        transformers=[
            ("tfidf", text_vectorizer, 0),  # column 0: raw text
            ("linguistic", linguistic_extractor, 0),
        ]
    )

    clf = LogisticRegression(
        max_iter=200,
        class_weight="balanced",
        n_jobs=-1,
    )

    pipeline = Pipeline(
        steps=[
            ("features", features),
            ("clf", clf),
        ]
    )
    return pipeline


def main() -> None:
    print("Ensuring NLTK data is available...")
    ensure_nltk_data()

    print(f"Loading data from {DATA_PATH}...")
    X, y = load_data(DATA_PATH)

    print("Splitting train/test...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    # ColumnTransformer expects a 2D array of shape (n_samples, n_features).
    X_train_2d = X_train.to_numpy().reshape(-1, 1)
    X_test_2d = X_test.to_numpy().reshape(-1, 1)

    print("Building pipeline (TF-IDF + 12 linguistic features + Logistic Regression)...")
    pipeline = build_pipeline()

    print("Training model...")
    pipeline.fit(X_train_2d, y_train)

    print("Evaluating on test set...")
    y_pred = pipeline.predict(X_test_2d)
    print(classification_report(y_test, y_pred))

    print(f"Saving model to {MODEL_PATH}...")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print("Done.")


if __name__ == "__main__":
    main()

