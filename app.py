import os
import joblib
import shap
from flask import Flask, render_template, request, jsonify
from textblob import TextBlob
from nrclex import NRCLex
import nltk

# Ensure NLTK data is ready
REQUIRED_NLTK_DATA = [
    'sentiment/vader_lexicon.zip',
    'corpora/wordnet.zip',
    'corpora/omw-1.4.zip',
    'tokenizers/punkt_tab.zip',
    'corpora/brown.zip',
    'taggers/averaged_perceptron_tagger_eng.zip'
]

for data in REQUIRED_NLTK_DATA:
    name = data.split('/')[-1].replace('.zip', '')
    try:
        nltk.data.find(data)
    except LookupError:
        print(f"Downloading nlt_data: {name}")
        nltk.download(name, quiet=True)

MODEL_PATH = "models/fake_review_model.joblib"

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(
            f"Model file not found at '{MODEL_PATH}'. "
            "Train the model first by running: python train_model.py"
        )
    return joblib.load(MODEL_PATH)

app = Flask(__name__)
model = load_model()

def _predict_proba_wrapped(texts):
    """Wrapper so the trained pipeline (which expects 2D input) works with SHAP."""
    X = [[t] for t in texts]
    return model.predict_proba(X)

# Initialize SHAP
explainer = shap.Explainer(_predict_proba_wrapped, shap.maskers.Text(r"\W+"))

def get_review_type(text, prob_fake):
    """Simple heuristic to categorize review character."""
    promo_keywords = ['buy', 'discount', 'limited', 'click', 'exclusive', 'offer', 'price', 'deal', 'promo', 'sales']
    spam_keywords = ['cash', 'win', 'money', 'free', 'opportunity', 'income', 'earn']
    
    words = text.lower().split()
    promo_count = sum(1 for w in words if w in promo_keywords)
    spam_count = sum(1 for w in words if w in spam_keywords)
    
    if prob_fake > 0.7:
        if promo_count > 1: return "Promotional / Commercial"
        if spam_count > 0: return "Potential Spam"
        return "Deceptive / Fake"
    elif prob_fake > 0.4:
        return "Highly Suspicious"
    else:
        return "Authentic / Genuine"

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze_review():
    data = request.json
    if not data or "review" not in data:
        return jsonify({"error": "No review text provided"}), 400

    review_text = data.get("review", "").strip()
    if not review_text:
        return jsonify({"error": "Empty review text provided"}), 400

    try:
        # 1. Base Fake/Real Prediction
        proba = _predict_proba_wrapped([review_text])[0]
        prob_fake = float(proba[1])
        prediction = "Fake" if prob_fake >= 0.5 else "Real"

        # 2. Sentiment Analysis (TextBlob)
        blob = TextBlob(review_text)
        polarity = blob.sentiment.polarity
        if polarity > 0.1: sentiment = "Positive"
        elif polarity < -0.1: sentiment = "Negative"
        else: sentiment = "Neutral"

        # 3. Emotion Analysis (NRCLex)
        emotion_obj = NRCLex(review_text)
        # Get the top emotion
        emotions = emotion_obj.top_emotions
        top_emotion = emotions[0][0] if emotions else "Neutral"
        # Map specific NRCLex tags to user-friendly ones
        emotion_map = {'trust': 'Confident', 'fear': 'Anxious', 'joy': 'Happy', 'anger': 'Angry', 
                       'sadness': 'Sad', 'disgust': 'Hate', 'surprise': 'Surprised', 'anticipation': 'Expectant'}
        friendly_emotion = emotion_map.get(top_emotion, top_emotion.capitalize())

        # 4. Review Type (Heuristic)
        review_type = get_review_type(review_text, prob_fake)

        # 5. SHAP Explanations
        shap_values_obj = explainer([review_text])
        tokens = shap_values_obj.data[0].tolist()
        values = shap_values_obj.values[0][:, 1].tolist()
        base_value = float(shap_values_obj.base_values[0][1])

        return jsonify({
            "success": True,
            "prediction": prediction,
            "confidence": prob_fake * 100 if prediction == "Fake" else (1 - prob_fake) * 100,
            "sentiment": sentiment,
            "emotion": friendly_emotion,
            "type": review_type,
            "explanation": list(zip(tokens, values)),
            "base_value": base_value
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)

