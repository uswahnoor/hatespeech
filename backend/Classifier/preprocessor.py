import spacy
import re
import json

class HateSpeechDetector:
    def __init__(self, json_path="hate_words.json",
                 replacement_word="worst",
                 model_path="transformer_classifier_checkpoint_best_best.pth",
                 tokenizer_path="tokenizer.json", rating_threshold=2):

        # Load hate words from JSON
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.hate_words = set(word.lower() for word in data.get("hate_words", []))

        self.replacement_word = replacement_word
        self.rating_threshold = rating_threshold

        # Load spaCy
        self.nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])

        # Initialize the transformer classifier
        from .utilities import TransformerClassifier
        import os
        # Convert relative paths to absolute paths if needed
        if not os.path.isabs(model_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, model_path)
        if not os.path.isabs(tokenizer_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            tokenizer_path = os.path.join(base_dir, tokenizer_path)
            
        self.classifier = TransformerClassifier(model_path, tokenizer_path)

    def preprocess_text(self, text):
        # Lowercase & remove URLs, mentions, hashtags
        text = re.sub(r"http\S+|www\S+|@\w+|#\w+", "", text.lower())

        # Replace hate words
        tokens = text.split()
        tokens = [self.replacement_word if t in self.hate_words else t for t in tokens]
        text = " ".join(tokens)

        # Lemmatization & stopword removal
        doc = self.nlp(text)
        tokens = [token.lemma_ for token in doc if not token.is_stop]

        return " ".join(tokens)

    def predict(self, text):
        clean_text = self.preprocess_text(text)
        label, confidence = self.classifier.predict(clean_text)
        sentiment = "negative" if label == 1 else "neutral"

        return label, confidence, sentiment
    

# example usage
# detector = HateSpeechDetector(json_path="hate_words.json",
#                               replacement_word="disgusting")

# text = "You are a filthy traitor and coward"
# label, confidence, sentiment = detector.predict(text)

# print("Hate:", label)          # 1 for hate, 0 for non-hate
# print("Confidence:", confidence)
# print("Sentiment:", sentiment)
