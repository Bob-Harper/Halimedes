import asyncio
import tkinter as tk
from tkinter import ttk
import subprocess

# Default settings
pitch = 100
speed = 1.0
test_phrase = "This is a test of my speech capabilities."
voice_path = "/home/msutt/hal/flitevox/cmu_us_rms.flitevox"  # Default voice file

# Voice options
voices = [
    {"name": "Andro", "file": "cmu_us_rxr.flitevox", "description": "Deeper, could be any gender"},
    {"name": "Indian Girl", "file": "cmu_us_axb.flitevox", "description": "Indian girl"},
    {"name": "Scottish with Static", "file": "cmu_us_clb.flitevox", "description": "Sort of Scottish but has a static burst at the start"},
    {"name": "Faint Scottish", "file": "cmu_us_eey.flitevox", "description": "Very faint Scottish, good thought for Stygia"},
    {"name": "Scottish Siri 1", "file": "cmu_us_ljm.flitevox", "description": "Scottish Siri"},
    {"name": "Scottish Siri 2", "file": "cmu_us_slt.flitevox", "description": "More Scottish Siri"},
    {"name": "Stephen Hawking", "file": "cmu_us_aew.flitevox", "description": "Stephen Hawking"},
    {"name": "Deeper Male", "file": "cmu_us_ahw.flitevox", "description": "Deeper, slightly Scottish"},
    {"name": "Higher Male", "file": "cmu_us_aup.flitevox", "description": "Higher pitch, slight Scottish"},
    {"name": "Scottish Hawking", "file": "cmu_us_awb.flitevox", "description": "Scottish Stephen Hawking"},
    {"name": "Natural Male", "file": "cmu_us_bdl.flitevox", "description": "More natural Stephen Hawking"},
    {"name": "Deeper Male 2", "file": "cmu_us_fem.flitevox", "description": "Deeper basic male"},
    {"name": "Quiet Scottish", "file": "cmu_us_gka.flitevox", "description": "Stronger Scottish, quiet volume"},
    {"name": "Deeper Quieter Male", "file": "cmu_us_jmk.flitevox", "description": "Deeper, softer, quieter"},
    {"name": "Scottish/Indian", "file": "cmu_us_ksp.flitevox", "description": "Much stronger Scottish/Indian"},
    {"name": "Default RMS", "file": "cmu_us_rms.flitevox", "description": "Slower, deeper (default)"},
]

# Speech function
async def speak_with_flite(phrase, pitch, speed, voice_path):
    """Speak the given phrase with specified pitch, speed, and voice file using Flite."""
    try:
        command = [
            "flite",
            "-voice", voice_path,
            "--setf", f"int_f0_target_mean={pitch}",
            "--setf", f"duration_stretch={speed}",
            "-t", phrase,
        ]
        await asyncio.to_thread(subprocess.run, command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error speaking: {e}")
    except FileNotFoundError:
        print("Flite command not found. Ensure it is installed and in the PATH.")

# GUI Application
class VoiceTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flite Voice Test")

        self.phrase_var = tk.StringVar(value="This is a test of my speech capabilities.")
        self.pitch_var = tk.DoubleVar(value=100.0)
        self.speed_var = tk.DoubleVar(value=1.0)
        self.selected_voice = tk.StringVar(value=voices[0]["file"])  # Default to first voice

        self.create_widgets()

    def create_widgets(self):
        """Create all widgets for the application."""
        tk.Label(self.root, text="Test Phrase:").grid(row=0, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.phrase_var, width=50).grid(row=0, column=1, columnspan=2)

        tk.Label(self.root, text="Pitch:").grid(row=1, column=0, sticky="w")
        tk.Scale(self.root, variable=self.pitch_var, from_=50, to=200, resolution=0.1, orient="horizontal").grid(row=1, column=1, sticky="ew")
        tk.Label(self.root, textvariable=self.pitch_var).grid(row=1, column=2)

        tk.Label(self.root, text="Speed:").grid(row=2, column=0, sticky="w")
        tk.Scale(self.root, variable=self.speed_var, from_=0.5, to=2.0, resolution=0.01, orient="horizontal").grid(row=2, column=1, sticky="ew")
        tk.Label(self.root, textvariable=self.speed_var).grid(row=2, column=2)

        tk.Label(self.root, text="Voice:").grid(row=3, column=0, sticky="w")
        voice_dropdown = ttk.Combobox(self.root, state="readonly", values=[v["description"] for v in voices])
        voice_dropdown.grid(row=3, column=1, columnspan=2, sticky="ew")
        voice_dropdown.bind("<<ComboboxSelected>>", self.update_voice)
        voice_dropdown.current(0)  # Set the default selection

        self.voice_file_label = tk.Label(self.root, text=self.selected_voice.get(), fg="blue")
        self.voice_file_label.grid(row=4, column=0, columnspan=3, sticky="w")

        tk.Button(self.root, text="Play", command=self.play_voice).grid(row=5, column=0, columnspan=3)

    def update_voice(self, event):
        """Update the selected voice and display the file."""
        selected_description = event.widget.get()
        selected_voice = next((v for v in voices if v["description"] == selected_description), None)
        if selected_voice:
            self.selected_voice.set(selected_voice["file"])
            self.voice_file_label.config(text=f"File: {selected_voice['file']}")

    def play_voice(self):
        """Trigger Flite with the current settings."""
        phrase = self.phrase_var.get()
        pitch = self.pitch_var.get()
        speed = self.speed_var.get()
        voice_file = self.selected_voice.get()
        voice_path = f"/home/msutt/hal/flitevox/{voice_file}"

        print(f"Voice Path: {voice_path}")  # Debug print
        asyncio.run(speak_with_flite(phrase, pitch, speed, voice_path))

# Main Program
if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceTestApp(root)
    root.mainloop()