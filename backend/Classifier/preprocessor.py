import re
from .custom_classifier import CustomHateSpeechClassifier

class HateSpeechDetector:
    def __init__(self, **kwargs):
        """
        Initialize the hate speech detector using the custom trained model.
        
        Uses the custom-trained model from the custom_model folder.
        """
        # Initialize the custom hate speech classifier
        self.classifier = CustomHateSpeechClassifier()

    def preprocess_text(self, text):
        """
        Minimal preprocessing - the model handles text understanding.
        
        Only removes URLs, mentions, and hashtags that could confuse the model.
        """
        # Remove URLs, mentions, and hashtags
        text = re.sub(r"http\S+|www\S+|@\w+|#\w+", "", text)
        # Remove extra whitespace
        text = " ".join(text.split())
        return text

    def predict(self, text):
        """
        Predict if text contains hate speech.
        
        Returns:
            tuple: (label, confidence, sentiment)
                - label: 1 for hate speech/offensive, 0 for safe
                - confidence: float between 0 and 1
                - sentiment: "negative" for hate/offensive, "positive" for safe
        """
        clean_text = self.preprocess_text(text)
        label, confidence = self.classifier.predict(clean_text)
        
        # sentiment: negative if label=1 (hate/offensive), positive if label=0 (safe)
        sentiment = "negative" if label == 1 else "positive"

        return label, confidence, sentiment
    

# example usage
# detector = HateSpeechDetector(json_path="hate_words.json",
#                               replacement_word="disgusting")

# text = "You are a filthy traitor and coward"
# label, confidence, sentiment = detector.predict(text)

# print("Hate:", label)          # 1 for hate, 0 for non-hate
# print("Confidence:", confidence)
# print("Sentiment:", sentiment)
