import os
import torch
import torchaudio


class VoiceprintManager:
    # Define default paths as class-level constants
    MODEL_PATH = "/home/msutt/hal/pyannote/embedding/pytorch_model.bin"
    VOICEPRINT_DIR = "/home/msutt/hal/voiceprints"

    def __init__(self):
        # Use class-level constants for paths
        self.model_path = self.MODEL_PATH
        self.voiceprint_dir = self.VOICEPRINT_DIR
        self.model = self._load_model()

    def _load_model(self):
        """Load the embedding model and its weights."""
        full_state_dict = torch.load(self.model_path, map_location=torch.device("cpu"))["state_dict"]

        from pyannote.audio.models.embedding import XVectorSincNet
        model = XVectorSincNet()

        # Filter and load state_dict
        filtered_state_dict = {k: v for k, v in full_state_dict.items() if k in model.state_dict()}
        model.load_state_dict(filtered_state_dict, strict=False)

        model.eval()
        return model

    def extract_embedding(self, audio_path):
        """Extract embedding from the given audio file."""
        try:
            # Load the audio file
            waveform, sample_rate = torchaudio.load(audio_path)

            # Convert stereo to mono if necessary
            if waveform.size(0) > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)

            # Resample to 16 kHz if needed
            if sample_rate != 16000:
                waveform = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)(waveform)

            # Extract embedding
            with torch.no_grad():
                embedding = self.model(waveform)

            return embedding
        except Exception as e:
            print(f"Error during embedding extraction: {e}")
            return None

    def save_embedding(self, audio_path, filename):
        """Extract and save embedding to a file."""
        save_path = os.path.join(self.voiceprint_dir, filename)
        embedding = self.extract_embedding(audio_path)
        if embedding is not None:
            torch.save(embedding, save_path)
            print(f"Embedding saved successfully to {save_path}")
        else:
            print("Failed to extract and save embedding.")

    def load_embedding(self, filename):
        """Load embedding from a file."""
        load_path = os.path.join(self.voiceprint_dir, filename)
        try:
            return torch.load(load_path)
        except Exception as e:
            print(f"Error loading embedding: {e}")
            return None

    def compare_embeddings(self, embedding1, embedding2):
        """Compare two embeddings and return a similarity score."""
        if embedding1 is None or embedding2 is None:
            print("One or both embeddings are missing.")
            return None

        similarity = torch.nn.functional.cosine_similarity(embedding1, embedding2).item()
        return similarity

    def extract_embedding_from_waveform(self, waveform):
        with torch.no_grad():
            return self.model(waveform)