"""
Vercel Serverless Function – /api/analyze
Pure Python Implementation without Scikit-Learn to guarantee < 250MB deployment size.
"""

import json
import os
import sys
import re
import math
from http.server import BaseHTTPRequestHandler

# ---------------------------------------------------------------------------
# NLTK setup – Vercel's filesystem is read-only except /tmp
# ---------------------------------------------------------------------------
NLTK_DATA_DIR = "/tmp/nltk_data"
os.environ["NLTK_DATA"] = NLTK_DATA_DIR
os.makedirs(NLTK_DATA_DIR, exist_ok=True)

import nltk
nltk.data.path.insert(0, NLTK_DATA_DIR)

REQUIRED_NLTK_DATA = [
    ("sentiment", "vader_lexicon"),
    ("corpora", "wordnet"),
    ("corpora", "omw-1.4"),
    ("tokenizers", "punkt_tab"),
    ("corpora", "brown"),
    ("taggers", "averaged_perceptron_tagger_eng"),
    ("corpora", "stopwords"),
]

for folder, name in REQUIRED_NLTK_DATA:
    try:
        nltk.data.find(f"{folder}/{name}")
    except LookupError:
        nltk.download(name, download_dir=NLTK_DATA_DIR, quiet=True)

from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer

_STOPWORDS = set(stopwords.words("english"))
_LEMMATIZER = WordNetLemmatizer()
_SIA = SentimentIntensityAnalyzer()

_MARKETING_WORDS = {
    "best", "amazing", "incredible", "fantastic", "perfect",
    "highly", "recommend", "unbelievable", "life-changing", "must-buy", "must-try",
}

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Load the pre-extracted JSON Model parameters
# ---------------------------------------------------------------------------
_model_params = None

def get_model_params():
    global _model_params
    if _model_params is None:
        path = os.path.join(PROJECT_ROOT, "models", "model_params.json")
        with open(path, "r", encoding="utf-8") as f:
            _model_params = json.load(f)
    return _model_params

# ---------------------------------------------------------------------------
# Preprocessing & Pure-Python TF-IDF Engine
# ---------------------------------------------------------------------------
def simple_preprocess(text: str) -> str:
    tokens = nltk.word_tokenize(text)
    cleaned = []
    for t in tokens:
        t_low = t.lower()
        if t_low.isalpha() and t_low not in _STOPWORDS:
            cleaned.append(_LEMMATIZER.lemmatize(t_low))
    return " ".join(cleaned)

def compute_tfidf(text: str, vocab: dict, idf: list):
    # Scikit-learn default token pattern
    tokens = re.findall(r"(?u)\b\w\w+\b", text)
    
    # 1-grams and 2-grams
    ngrams = list(tokens)
    for i in range(len(tokens) - 1):
        ngrams.append(tokens[i] + " " + tokens[i+1])
        
    tf = {}
    for ng in ngrams:
        tf[ng] = tf.get(ng, 0) + 1
        
    vec = {}
    for ng, count in tf.items():
        if ng in vocab:
            idx = vocab[ng]
            vec[idx] = count * idf[idx]
            
    norm = math.sqrt(sum(v*v for v in vec.values()))
    if norm > 0:
        for idx in vec:
            vec[idx] /= norm
    return vec

# ---------------------------------------------------------------------------
# Linguistic Features Engine
# ---------------------------------------------------------------------------
def compute_linguistic_features(text: str):
    tokens = word_tokenize(text)
    token_count = len(tokens)
    chars = len(text)
    words = [t for t in tokens if any(c.isalpha() for c in t)]

    review_length = token_count
    avg_word_length = (sum(len(w) for w in words) / len(words)) if words else 0.0
    exclamation_count = text.count("!")
    capital_chars = sum(1 for c in text if c.isupper())
    capital_ratio = (capital_chars / chars) if chars > 0 else 0.0
    sentiment_score = _SIA.polarity_scores(text)["compound"]

    tagged = pos_tag(tokens) if tokens else []
    adj_count = sum(1 for _, tag in tagged if tag.startswith("JJ"))
    adjective_ratio = (adj_count / token_count) if token_count > 0 else 0.0

    adv_count = sum(1 for _, tag in tagged if tag.startswith("RB"))
    adverb_ratio = (adv_count / token_count) if token_count > 0 else 0.0

    pronoun_tags = {"PRP", "PRP$", "WP", "WP$"}
    pronoun_count = sum(1 for _, tag in tagged if tag in pronoun_tags)

    word_tokens = [w.lower() for w in words]
    unique_word_ratio = (len(set(word_tokens)) / len(word_tokens)) if word_tokens else 0.0

    stop_count = sum(1 for w in word_tokens if w in _STOPWORDS)
    stopword_ratio = (stop_count / len(word_tokens)) if word_tokens else 0.0

    punctuation_count = len(re.findall(r"[^\w\s]", text))
    marketing_word_count = sum(1 for w in word_tokens if w in _MARKETING_WORDS)

    return [
        float(review_length), float(avg_word_length), float(exclamation_count), float(capital_ratio),
        float(sentiment_score), float(adjective_ratio), float(adverb_ratio), float(pronoun_count),
        float(unique_word_ratio), float(stopword_ratio), float(punctuation_count), float(marketing_word_count),
    ]

def get_review_type(text, prob_fake):
    promo_keywords = ['buy', 'discount', 'limited', 'click', 'exclusive', 'offer', 'price', 'deal', 'promo', 'sales']
    spam_keywords = ['cash', 'win', 'money', 'free', 'opportunity', 'income', 'earn']
    words = text.lower().split()
    promo_count = sum(1 for w in words if w in promo_keywords)
    spam_count = sum(1 for w in words if w in spam_keywords)
    if prob_fake > 0.7:
        if promo_count > 1: return "Promotional / Commercial"
        if spam_count > 0: return "Potential Spam"
        return "Deceptive / Fake"
    elif prob_fake > 0.4: return "Highly Suspicious"
    else: return "Authentic / Genuine"

# ---------------------------------------------------------------------------
# Vercel HTTP Handler
# ---------------------------------------------------------------------------
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body) if body else {}
        except (json.JSONDecodeError, ValueError):
            self._respond(400, {"error": "Invalid JSON body"})
            return

        review_text = (data.get("review") or "").strip()
        if not review_text:
            self._respond(400, {"error": "No review text provided"})
            return

        try:
            from textblob import TextBlob
            from nrclex import NRCLex

            params = get_model_params()
            vocab = params['vocab']
            idf = params['idf']
            coef = params['coef']
            intercept = params['intercept']

            # 1. Feature Extraction (Pure Python)
            preprocessed_text = simple_preprocess(review_text)
            tfidf_vec = compute_tfidf(preprocessed_text, vocab, idf)
            ling_features = compute_linguistic_features(review_text)

            # 2. Logistic Regression Math
            logit = intercept
            for idx, val in tfidf_vec.items():
                logit += val * coef[idx]
            
            vocab_size = len(vocab)
            for i, val in enumerate(ling_features):
                logit += val * coef[vocab_size + i]

            prob_fake = 1.0 / (1.0 + math.exp(-logit))
            prediction = "Fake" if prob_fake >= 0.5 else "Real"

            # 3. Sentiment & Emotion Analysis
            blob = TextBlob(review_text)
            polarity = blob.sentiment.polarity
            sentiment = "Positive" if polarity > 0.1 else ("Negative" if polarity < -0.1 else "Neutral")

            emotion_obj = NRCLex(review_text)
            emotions = emotion_obj.top_emotions
            top_emotion = emotions[0][0] if emotions else "Neutral"
            emotion_map = {
                'trust': 'Confident', 'fear': 'Anxious', 'joy': 'Happy',
                'anger': 'Angry', 'sadness': 'Sad', 'disgust': 'Hate',
                'surprise': 'Surprised', 'anticipation': 'Expectant',
            }
            friendly_emotion = emotion_map.get(top_emotion, top_emotion.capitalize())

            # 4. Native Linear Explanations
            tokens = re.findall(r"\w+|\W+", review_text)
            explanation = []

            for token in tokens:
                word = token.lower()
                score = 0.0
                if word in vocab:
                    idx = vocab[word]
                    score = float(coef[idx]) * 0.2
                explanation.append((token, score))

            self._respond(200, {
                "success": True,
                "prediction": prediction,
                "confidence": prob_fake * 100 if prediction == "Fake" else (1 - prob_fake) * 100,
                "sentiment": sentiment,
                "emotion": friendly_emotion,
                "type": get_review_type(review_text, prob_fake),
                "explanation": explanation,
                "base_value": intercept,
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            self._respond(500, {"success": False, "error": str(e)})

    def do_GET(self):
        self._respond(200, {"status": "ok", "message": "Fake Review Detection API is running (Pure Python)."})

    def _respond(self, status_code, payload):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
