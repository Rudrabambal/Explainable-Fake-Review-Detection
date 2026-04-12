import re
from typing import List

import numpy as np
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from scipy.sparse import csr_matrix
from sklearn.base import BaseEstimator, TransformerMixin


def _load_stopwords():
    try:
        return set(stopwords.words("english"))
    except LookupError:
        import nltk

        nltk.download("stopwords", quiet=True)
        return set(stopwords.words("english"))


def _load_sia():
    try:
        return SentimentIntensityAnalyzer()
    except LookupError:
        import nltk

        nltk.download("vader_lexicon", quiet=True)
        return SentimentIntensityAnalyzer()


_STOPWORDS = _load_stopwords()
_SIA = _load_sia()


_MARKETING_WORDS = {
    "best",
    "amazing",
    "incredible",
    "fantastic",
    "perfect",
    "highly",
    "recommend",
    "unbelievable",
    "life-changing",
    "must-buy",
    "must-try",
}


class LinguisticFeatureExtractor(BaseEstimator, TransformerMixin):
    """Compute 12 handcrafted linguistic features from raw review text."""

    def fit(self, X: List[str], y=None):
        return self

    def transform(self, X: List[str]) -> csr_matrix:
        rows = [self._features_for_text(text) for text in X]
        return csr_matrix(np.array(rows, dtype=float))

    def _features_for_text(self, text: str) -> List[float]:
        if not isinstance(text, str):
            text = "" if text is None else str(text)

        tokens = word_tokenize(text)
        token_count = len(tokens)
        chars = len(text)
        words = [t for t in tokens if any(c.isalpha() for c in t)]

        # review_length
        review_length = token_count

        # avg_word_length
        avg_word_length = (sum(len(w) for w in words) / len(words)) if words else 0.0

        # exclamation_count
        exclamation_count = text.count("!")

        # capital_ratio
        capital_chars = sum(1 for c in text if c.isupper())
        capital_ratio = (capital_chars / chars) if chars > 0 else 0.0

        # sentiment_score (compound score from VADER)
        sentiment_score = _SIA.polarity_scores(text)["compound"]

        # POS tagging
        tagged = pos_tag(tokens) if tokens else []

        # adjective_ratio
        adj_count = sum(1 for _, tag in tagged if tag.startswith("JJ"))
        adjective_ratio = (adj_count / token_count) if token_count > 0 else 0.0

        # adverb_ratio
        adv_count = sum(1 for _, tag in tagged if tag.startswith("RB"))
        adverb_ratio = (adv_count / token_count) if token_count > 0 else 0.0

        # pronoun_count (personal + possessive pronouns)
        pronoun_tags = {"PRP", "PRP$", "WP", "WP$"}
        pronoun_count = sum(1 for _, tag in tagged if tag in pronoun_tags)

        # unique_word_ratio
        word_tokens = [w.lower() for w in words]
        unique_word_ratio = (len(set(word_tokens)) / len(word_tokens)) if word_tokens else 0.0

        # stopword_ratio
        stop_count = sum(1 for w in word_tokens if w in _STOPWORDS)
        stopword_ratio = (stop_count / len(word_tokens)) if word_tokens else 0.0

        # punctuation_count
        punctuation_count = len(re.findall(r"[^\w\s]", text))

        # marketing_word_count
        marketing_word_count = sum(1 for w in word_tokens if w in _MARKETING_WORDS)

        return [
            float(review_length),
            float(avg_word_length),
            float(exclamation_count),
            float(capital_ratio),
            float(sentiment_score),
            float(adjective_ratio),
            float(adverb_ratio),
            float(pronoun_count),
            float(unique_word_ratio),
            float(stopword_ratio),
            float(punctuation_count),
            float(marketing_word_count),
        ]

