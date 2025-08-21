"""Text preprocessing utilities using NLTK and spaCy with graceful fallbacks.

Features:
- Basic cleaning: lowercasing, URL/mention/hashtag/email/html removal, punctuation & number stripping
- Tokenization
- Stopword removal (NLTK)
- Lemmatization (spaCy if available, else NLTK WordNet)

This module avoids crashing if resources are missing and falls back to minimal behavior.
"""

from __future__ import annotations

import re
import unicodedata
from typing import List, Optional

# NLTK setup
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    _NLTK_OK = True
except Exception:  # pragma: no cover
    nltk = None  # type: ignore
    stopwords = None  # type: ignore
    WordNetLemmatizer = None  # type: ignore
    _NLTK_OK = False

# spaCy setup
try:
    import spacy
    _SPACY_OK = True
except Exception:  # pragma: no cover
    spacy = None  # type: ignore
    _SPACY_OK = False

_STOPWORDS: set[str] = set()
_WORDNET: Optional[WordNetLemmatizer] = None  # type: ignore
_NLP = None  # spaCy nlp object


def _ensure_nltk():
    global _STOPWORDS, _WORDNET
    if not _NLTK_OK:
        return
    try:
        # Ensure resources; download quietly if missing
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:  # pragma: no cover
            nltk.download('stopwords', quiet=True)
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:  # pragma: no cover
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
        _STOPWORDS = set(stopwords.words('english'))
        _WORDNET = WordNetLemmatizer()
    except Exception:  # pragma: no cover
        # Fallback to a tiny stopword set
        _STOPWORDS = {"the", "a", "an", "and", "or", "is", "are", "to", "in", "of"}
        _WORDNET = None


def _ensure_spacy():
    global _NLP
    if not _SPACY_OK:
        return
    if _NLP is not None:
        return
    try:
        # Try small English model; fallback to blank English pipeline
        _NLP = spacy.load('en_core_web_sm', disable=['ner'])
    except Exception:  # pragma: no cover
        try:
            _NLP = spacy.blank('en')
            # Add simple components if available
            if 'lemmatizer' not in _NLP.pipe_names:
                # spaCy v3 lemmatizer may require lookups; ignore if unavailable
                pass
        except Exception:
            _NLP = None


class TextPreprocessor:
    URL_RE = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
    HTML_RE = re.compile(r"<[^>]+>")
    MENTION_RE = re.compile(r"@[A-Za-z0-9_]+")
    HASHTAG_RE = re.compile(r"#[A-Za-z0-9_]+")
    EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}")
    PUNCT_NUM_RE = re.compile(r"[^A-Za-z\s]")
    MULTISPACE_RE = re.compile(r"\s+")

    def __init__(self):
        _ensure_nltk()
        _ensure_spacy()

    @staticmethod
    def normalize_unicode(text: str) -> str:
        return unicodedata.normalize('NFKC', text)

    def basic_clean(self, text: str) -> str:
        text = self.normalize_unicode(text)
        text = text.lower()
        text = self.URL_RE.sub(" ", text)
        text = self.EMAIL_RE.sub(" ", text)
        text = self.MENTION_RE.sub(" ", text)
        text = self.HASHTAG_RE.sub(" ", text)
        text = self.HTML_RE.sub(" ", text)
        text = self.PUNCT_NUM_RE.sub(" ", text)  # remove punctuation & digits
        text = self.MULTISPACE_RE.sub(" ", text).strip()
        return text

    def tokenize(self, text: str) -> List[str]:
        if _NLP is not None:
            doc = _NLP.make_doc(text)
            return [t.text for t in doc if t.text.strip()]
        # simple whitespace tokenization
        return [t for t in text.split() if t]

    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        if _STOPWORDS:
            return [t for t in tokens if t not in _STOPWORDS]
        return tokens

    def lemmatize(self, tokens: List[str]) -> List[str]:
        if _NLP is not None:
            # Use spaCy lemmatization if possible
            doc = _NLP(" ".join(tokens))
            lemmas = [t.lemma_ if t.lemma_ not in ("-PRON-", " ") else t.text for t in doc]
            return [l for l in lemmas if l]
        if _WORDNET is not None:
            return [_WORDNET.lemmatize(t) for t in tokens]
        return tokens

    def preprocess(self, text: str) -> dict:
        cleaned = self.basic_clean(text)
        tokens = self.tokenize(cleaned)
        tokens_ns = self.remove_stopwords(tokens)
        lemmas = self.lemmatize(tokens_ns)
        return {
            "original": text,
            "cleaned": cleaned,
            "tokens": tokens_ns,
            "lemmas": lemmas,
        }


# Singleton-style helper
_PREPROCESSOR: Optional[TextPreprocessor] = None


def get_preprocessor() -> TextPreprocessor:
    global _PREPROCESSOR
    if _PREPROCESSOR is None:
        _PREPROCESSOR = TextPreprocessor()
    return _PREPROCESSOR
