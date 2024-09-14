from sentence_transformers import SentenceTransformer

model = SentenceTransformer('distilroberta-base-msmarco-v2')

def encode_text(text: str):
    news_text = f"news article: {text}"
    return model.encode(news_text).tolist()