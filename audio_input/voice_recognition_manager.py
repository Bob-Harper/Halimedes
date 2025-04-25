import os
import torch
import torchaudio


class VoiceRecognitionManager:
    MODEL_PATH = "/home/msutt/hal/pyannote/embedding/pytorch_model.bin"
    VOICEPRINT_DIR = "/home/msutt/hal/voiceprints"

    def __init__(self):
        self.model_path = self.MODEL_PATH
        self.voiceprint_dir = self.VOICEPRINT_DIR
        self.model = self._load_model()
        # Load all known speaker embeddings here
        self.embeddings = {
            "Dad": self.load_embedding("dad_embedding.pt"),
            "Onnalyn": self.load_embedding("onnalyn_embedding.pt"),
            # Add more speakers here as needed
        }
        self.threshold = 0.2  # If highest similarity is below this, treat speaker as Unknown.

    def recognize_speaker(self, raw_audio):
        """
        Recognize the speaker by processing raw audio directly.
        1. Convert raw audio to a waveform.
        2. Extract the embedding.
        3. Compare it against known embeddings.
        """
        try:
            # Step 1: Convert raw audio to waveform
            waveform = self.convert_raw_to_waveform(raw_audio)
            
            # Step 2: Extract the new embedding from waveform
            new_embedding = self.extract_embedding_from_waveform(waveform)
            
            # Step 3: Perform the comparison as before
            best_speaker = "Unknown"
            best_score = -1.0

            for speaker_name, ref_embedding in self.embeddings.items():
                if ref_embedding is not None:
                    similarity = self.compare_embeddings(new_embedding, ref_embedding)
                    if similarity and similarity > best_score:
                        best_score = similarity
                        best_speaker = speaker_name

            if best_score >= self.threshold:
                return best_speaker
            return "Unknown"
        
        except Exception as e:
            print(f"Error during speaker recognition: {e}")
            return "Unknown"
    
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
        
    @staticmethod    
    def convert_raw_to_waveform(raw_audio):
        # Process the raw audio to extract waveform
        waveform = torch.tensor(raw_audio, dtype=torch.float32).unsqueeze(0) / 32768.0  # Normalize [-1, 1]
        if waveform.dim() == 2:
            waveform = waveform.unsqueeze(1)  # Add batch dimension if needed

        # Resample audio to 16 kHz for voiceprint
        waveform = torchaudio.transforms.Resample(orig_freq=44100, new_freq=16000)(waveform)

        return waveform
