import torch
import torch.nn as nn
import math
import os
from tokenizers import Tokenizer
from tokenizers.processors import BertProcessing

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=512):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        return x + self.pe[:, :x.size(1)]

class TransformerInputLayer(nn.Module):
    def __init__(self, vocab_size, d_model, max_len=256, dropout=0.1):
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.positional_encoding = PositionalEncoding(d_model, max_len)
        self.dropout = nn.Dropout(dropout)

    def forward(self, input_ids):
        x = self.token_embedding(input_ids)
        x = self.positional_encoding(x)
        return self.dropout(x)

class MultiHeadSelfAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        assert d_model % num_heads == 0
        self.d_k = d_model // num_heads
        self.num_heads = num_heads
        self.q_linear = nn.Linear(d_model, d_model)
        self.k_linear = nn.Linear(d_model, d_model)
        self.v_linear = nn.Linear(d_model, d_model)
        self.out_linear = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x, mask=None):
        B, T, D = x.size()
        Q = self.q_linear(x).view(B, T, self.num_heads, self.d_k).transpose(1, 2)
        K = self.k_linear(x).view(B, T, self.num_heads, self.d_k).transpose(1, 2)
        V = self.v_linear(x).view(B, T, self.num_heads, self.d_k).transpose(1, 2)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        attn = torch.softmax(scores, dim=-1)
        out = torch.matmul(self.dropout(attn), V)
        out = out.transpose(1, 2).contiguous().view(B, T, D)
        return self.out_linear(out)

class FeedForward(nn.Module):
    def __init__(self, d_model, d_ff):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.relu1 = nn.ReLU()
        self.linear2 = nn.Linear(d_ff, d_ff//2)
        self.relu2 = nn.ReLU()
        self.linear3 = nn.Linear(d_ff//2, d_model)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x):
        return self.linear3(self.dropout(self.relu2(self.linear2(self.relu1(self.linear1(x))))))

class TransformerEncoderBlock(nn.Module):
    def __init__(self, d_model, num_heads, d_ff):
        super().__init__()
        self.attn = MultiHeadSelfAttention(d_model, num_heads)
        self.norm1 = nn.LayerNorm(d_model)
        self.ff = FeedForward(d_model, d_ff)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x, mask=None):
        attn_out = self.attn(x, mask)
        x = self.norm1(x + self.dropout(attn_out))
        ff_out = self.ff(x)
        return self.norm2(x + self.dropout(ff_out))

class TransformerEncoder(nn.Module):
    def __init__(self, vocab_size, d_model, num_heads, d_ff, num_layers, max_len, dropout):
        super().__init__()
        self.input_layer = TransformerInputLayer(vocab_size, d_model, max_len, dropout)
        self.layers = nn.ModuleList([
            TransformerEncoderBlock(d_model, num_heads, d_ff)
            for _ in range(num_layers)
        ])

    def forward(self, input_ids, mask=None):
        x = self.input_layer(input_ids)
        for layer in self.layers:
            x = layer(x, mask)
        return x

MODEL_CONFIG = {
    'D_MODEL': 128,
    'NUM_HEADS': 4,
    'D_FF': 512,
    'NUM_LAYERS': 2,
    'MAX_LEN': 256,
    'DROPOUT': 0.1,
    'NUM_CLASSES': 5,
    'VOCAB_SIZE': 30000
}

class TransformerClassifier:
    def __init__(self, model_path, tokenizer_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load tokenizer
        if not os.path.exists(tokenizer_path):
            raise FileNotFoundError(f"Tokenizer file not found: {tokenizer_path}")
        self.tokenizer = Tokenizer.from_file(tokenizer_path)
        self.tokenizer.post_processor = BertProcessing(
            ("[SEP]", self.tokenizer.token_to_id("[SEP]")),
            ("[CLS]", self.tokenizer.token_to_id("[CLS]"))
        )
        self.tokenizer.enable_truncation(max_length=MODEL_CONFIG['MAX_LEN'])
        self.tokenizer.enable_padding(
            length=MODEL_CONFIG['MAX_LEN'],
            pad_id=self.tokenizer.token_to_id("[PAD]"),
            pad_token="[PAD]"
        )
        
        # Initialize model
        vocab_size = self.tokenizer.get_vocab_size()
        self.model = nn.ModuleDict({
            'encoder': TransformerEncoder(
                vocab_size=vocab_size,
                d_model=MODEL_CONFIG['D_MODEL'],
                num_heads=MODEL_CONFIG['NUM_HEADS'],
                d_ff=MODEL_CONFIG['D_FF'],
                num_layers=MODEL_CONFIG['NUM_LAYERS'],
                max_len=MODEL_CONFIG['MAX_LEN'],
                dropout=MODEL_CONFIG['DROPOUT']
            ),
            'classifier': nn.Linear(MODEL_CONFIG['D_MODEL'], MODEL_CONFIG['NUM_CLASSES'])
        })
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

    def predict(self, text):
        # Tokenize input
        enc = self.tokenizer.encode(text)
        input_ids = torch.tensor([enc.ids]).to(self.device)
        
        # Get prediction
        with torch.no_grad():
            encoded = self.model['encoder'](input_ids)
            cls_output = encoded[:, 0, :]  # Take [CLS] token output
            logits = self.model['classifier'](cls_output)
            probs = torch.softmax(logits, dim=1)
            prediction = torch.argmax(probs, dim=1).item()
            confidence = probs[0][prediction].item()

            is_hate = prediction <= 1
            hate_confidence = sum(probs[0][:2].tolist()) if is_hate else sum(probs[0][2:].tolist())
            
        return int(is_hate), float(hate_confidence)

class HateSpeechDetector:
    def __init__(self, model_path="transformer_classifier_checkpoint_best_best.pth",
                 tokenizer_path="tokenizer.json"):
        self.classifier = TransformerClassifier(model_path, tokenizer_path)

    def predict(self, text):

        label, confidence = self.classifier.predict(text)
        sentiment = "negative" if label == 1 else "neutral"
        
        return label, confidence, sentiment
    
# example usage
# # Initialize once
# detector = HateSpeechDetector()

# # Predict
# label, conf, sentiment = detector.predict("Those people are disgusting animals.")
# print(f"Prediction: {'Hate' if label else 'Non-Hate'}")
# print(f"Sentiment: {sentiment}")
# print(f"Confidence: {conf:.2%}")

# label, conf, sentiment = detector.predict("I love spending time with everyone.")
# print(f"Prediction: {'Hate' if label else 'Non-Hate'}")
# print(f"Sentiment: {sentiment}")
# print(f"Confidence: {conf:.2%}")
