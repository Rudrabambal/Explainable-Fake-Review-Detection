import os

import joblib
from flask import Flask, render_template_string, request
from lime.lime_text import LimeTextExplainer


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
    """Wrapper so the trained pipeline (which expects 2D input) works with LIME."""
    X = [[t] for t in texts]  # shape (n_samples, 1)
    return model.predict_proba(X)


CLASS_NAMES = ["Real", "Fake"]
explainer = LimeTextExplainer(class_names=CLASS_NAMES)


TEMPLATE = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Explainable Fake Review Detection</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 40px; background: #f5f7fb; }
      h1 { color: #333; }
      .container { max-width: 900px; margin: 0 auto; }
      textarea { width: 100%; height: 150px; padding: 10px; font-size: 14px; }
      button { padding: 10px 20px; font-size: 14px; background: #2563eb; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
      button:hover { background: #1d4ed8; }
      .result { margin-top: 20px; padding: 15px; border-radius: 4px; background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
      .fake { border-left: 4px solid #dc2626; }
      .real { border-left: 4px solid #16a34a; }
      .prob { font-weight: bold; }
      .lime-html { margin-top: 20px; }
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Explainable Fake Review Detection</h1>
      <form method="post">
        <label for="review">Enter a review:</label><br>
        <textarea id="review" name="review" required>{{ review_text }}</textarea><br><br>
        <button type="submit">Analyze</button>
      </form>

      {% if prediction is not none %}
      <div class="result {{ 'fake' if prediction == 'Fake' else 'real' }}">
        <p><strong>Prediction:</strong> {{ prediction }}</p>
        <p class="prob">Fake probability: {{ prob_fake | round(3) }}</p>
      </div>

      <div class="lime-html">
        <h3>Explanation (LIME)</h3>
        {{ lime_html|safe }}
      </div>
      {% endif %}
    </div>
  </body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    review_text = ""
    prediction = None
    prob_fake = None
    lime_html = ""

    if request.method == "POST":
        review_text = request.form.get("review", "")
        if review_text.strip():
            proba = _predict_proba_wrapped([review_text])[0]
            # Assume label 1 corresponds to Fake; adjust if your dataset differs
            prob_fake = float(proba[1])
            prediction = "Fake" if prob_fake >= 0.5 else "Real"

            exp = explainer.explain_instance(
                review_text,
                _predict_proba_wrapped,
                num_features=10,
                labels=[1],  # focus on "Fake" class
            )
            lime_html = exp.as_html(labels=[1])

    return render_template_string(
        TEMPLATE,
        review_text=review_text,
        prediction=prediction,
        prob_fake=prob_fake,
        lime_html=lime_html,
    )


if __name__ == "__main__":
    app.run(debug=True)

