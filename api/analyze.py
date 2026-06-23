"""
Vercel Serverless Function – /api/analyze
Replaces the Flask backend for Vercel deployment.
"""

import json
import os
import sys
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

# ---------------------------------------------------------------------------
# Add project root to sys.path so we can import features / preprocessing
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Lazy-loaded heavy imports (cached across warm invocations)
# ---------------------------------------------------------------------------
_model = None
_explainer = None


def _get_model():
    global _model
    if _model is None:
        import joblib
        model_path = os.path.join(PROJECT_ROOT, "models", "fake_review_model.joblib")
        if not os.path.exists(model_path):
            raise RuntimeError(f"Model file not found at '{model_path}'.")
        _model = joblib.load(model_path)
    return _model


def _predict_proba_wrapped(texts):
    """Wrapper so the trained pipeline (which expects 2D input) works with SHAP."""
    model = _get_model()
    X = [[t] for t in texts]
    return model.predict_proba(X)


def _get_explainer():
    global _explainer
    if _explainer is None:
        import shap
        _explainer = shap.Explainer(_predict_proba_wrapped, shap.maskers.Text(r"\W+"))
    return _explainer


def get_review_type(text, prob_fake):
    """Simple heuristic to categorize review character."""
    promo_keywords = ['buy', 'discount', 'limited', 'click', 'exclusive', 'offer', 'price', 'deal', 'promo', 'sales']
    spam_keywords = ['cash', 'win', 'money', 'free', 'opportunity', 'income', 'earn']

    words = text.lower().split()
    promo_count = sum(1 for w in words if w in promo_keywords)
    spam_count = sum(1 for w in words if w in spam_keywords)

    if prob_fake > 0.7:
        if promo_count > 1:
            return "Promotional / Commercial"
        if spam_count > 0:
            return "Potential Spam"
        return "Deceptive / Fake"
    elif prob_fake > 0.4:
        return "Highly Suspicious"
    else:
        return "Authentic / Genuine"


# ---------------------------------------------------------------------------
# Vercel handler
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

            # 1. Base Fake/Real Prediction
            proba = _predict_proba_wrapped([review_text])[0]
            prob_fake = float(proba[1])
            prediction = "Fake" if prob_fake >= 0.5 else "Real"

            # 2. Sentiment Analysis (TextBlob)
            blob = TextBlob(review_text)
            polarity = blob.sentiment.polarity
            if polarity > 0.1:
                sentiment = "Positive"
            elif polarity < -0.1:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

            # 3. Emotion Analysis (NRCLex)
            emotion_obj = NRCLex(review_text)
            emotions = emotion_obj.top_emotions
            top_emotion = emotions[0][0] if emotions else "Neutral"
            emotion_map = {
                'trust': 'Confident', 'fear': 'Anxious', 'joy': 'Happy',
                'anger': 'Angry', 'sadness': 'Sad', 'disgust': 'Hate',
                'surprise': 'Surprised', 'anticipation': 'Expectant',
            }
            friendly_emotion = emotion_map.get(top_emotion, top_emotion.capitalize())

            # 4. Review Type (Heuristic)
            review_type = get_review_type(review_text, prob_fake)

            # 5. SHAP Explanations
            explainer = _get_explainer()
            shap_values_obj = explainer([review_text])
            tokens = shap_values_obj.data[0].tolist()
            values = shap_values_obj.values[0][:, 1].tolist()
            base_value = float(shap_values_obj.base_values[0][1])

            self._respond(200, {
                "success": True,
                "prediction": prediction,
                "confidence": prob_fake * 100 if prediction == "Fake" else (1 - prob_fake) * 100,
                "sentiment": sentiment,
                "emotion": friendly_emotion,
                "type": review_type,
                "explanation": list(zip(tokens, values)),
                "base_value": base_value,
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            self._respond(500, {"success": False, "error": str(e)})

    def do_GET(self):
        self._respond(200, {"status": "ok", "message": "Fake Review Detection API is running."})

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
