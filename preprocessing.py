import os
from typing import Iterable, List

# Configure NLTK data path for Vercel serverless (read-only filesystem)
_NLTK_DATA_DIR = os.environ.get("NLTK_DATA", "/tmp/nltk_data")
os.makedirs(_NLTK_DATA_DIR, exist_ok=True)

import nltk
nltk.data.path.insert(0, _NLTK_DATA_DIR)

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


_NLTK_PACKAGES = ["punkt", "stopwords", "wordnet", "averaged_perceptron_tagger", "vader_lexicon"]


def ensure_nltk_data() -> None:
    """Download required NLTK data packages if missing."""
    for pkg in _NLTK_PACKAGES:
        try:
            nltk.data.find(f"corpora/{pkg}")
        except LookupError:
            try:
                nltk.download(pkg, download_dir=_NLTK_DATA_DIR, quiet=True)
            except Exception:
                # Best-effort; if offline, downstream code may raise a clearer error.
                pass


_STOPWORDS = set(stopwords.words("english"))
_LEMMATIZER = WordNetLemmatizer()


def simple_preprocess(text: str) -> str:
    """Basic cleanup + tokenization + lowercasing + stopword removal + lemmatization."""
    if not isinstance(text, str):
        text = "" if text is None else str(text)

    tokens = nltk.word_tokenize(text)
    cleaned: List[str] = []
    for t in tokens:
        t_low = t.lower()
        if t_low.isalpha() and t_low not in _STOPWORDS:
            cleaned.append(_LEMMATIZER.lemmatize(t_low))
    return " ".join(cleaned)


def preprocess_corpus(texts: Iterable[str]) -> List[str]:
    """Apply simple_preprocess to an iterable of texts."""
    return [simple_preprocess(t) for t in texts]

