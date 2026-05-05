import spacy
import asyncio

class Embedder:
    def __init__(self):
        # Load spaCy model once at startup
        self.nlp = spacy.load("en_core_web_md")

    def embed(self, text: str) -> list[float]:
        doc = self.nlp(text)
        return doc.vector.tolist()

    def _embed_sync(self, text: str) -> list[float]:
        doc = self.nlp(text)
        return doc.vector.tolist()
