"""
Text-to-Speech GUI (offline, Windows 11 / SAPI5 via pyttsx3)

A simple desktop app for non-technical users: type or paste text, pick a voice,
adjust speed and volume, and save the result as a .wav audio file.

Dependencies: pyttsx3 (plus its automatic deps pywin32 and comtypes on Windows).
No ffmpeg required. Output format is WAV.
"""

import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyttsx3


def synthesize(text, output_file, rate, volume, voice_id):
    """
    Core text-to-speech work. Runs on a background thread so the GUI
    stays responsive. Creates its own engine instance per call, which
    avoids the known pyttsx3 issue of reusing an engine across multiple
    runAndWait() calls in one process.
    """
    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.setProperty("volume", max(0.0, min(1.0, volume)))
    if voice_id:
        engine.setProperty("voice", voice_id)
    engine.save_to_file(text, output_file)
    engine.runAndWait()


class TTSApp:
    def __init__(self, root):
        self.root = root
        root.title("Text to Speech")
        root.geometry("520x440")
        root.resizable(False, False)

        # Load installed voices once, for the dropdown.
        try:
            probe = pyttsx3.init()
            self.voices = probe.getProperty("voices")
        except Exception as e:
            messagebox.showerror("Error", f"Could not start the speech engine:\n{e}")
            self.voices = []

        pad = {"padx": 12, "pady": 6}

        # --- Text input ---
        tk.Label(root, text="Enter text to convert:").pack(anchor="w", **pad)
        self.text_box = tk.Text(root, height=8, wrap="word")
        self.text_box.pack(fill="x", padx=12)
        self.text_box.insert("1.0", "This is a test of the text to speech function.")

        # --- Voice dropdown ---
        voice_frame = tk.Frame(root)
        voice_frame.pack(fill="x", **pad)
        tk.Label(voice_frame, text="Voice:").pack(side="left")
        self.voice_names = [v.name for v in self.voices] or ["(default)"]
        self.voice_choice = ttk.Combobox(
            voice_frame, values=self.voice_names, state="readonly", width=40
        )
        self.voice_choice.current(0)
        self.voice_choice.pack(side="left", padx=8)

        # --- Rate slider ---
        rate_frame = tk.Frame(root)
        rate_frame.pack(fill="x", **pad)
        tk.Label(rate_frame, text="Speed:").pack(side="left")
        self.rate = tk.IntVar(value=180)
        tk.Scale(rate_frame, from_=80, to=300, orient="horizontal",
                 variable=self.rate, length=320).pack(side="left", padx=8)

        # --- Volume slider ---
        vol_frame = tk.Frame(root)
        vol_frame.pack(fill="x", **pad)
        tk.Label(vol_frame, text="Volume:").pack(side="left")
        self.volume = tk.DoubleVar(value=1.0)
        tk.Scale(vol_frame, from_=0.0, to=1.0, resolution=0.1, orient="horizontal",
                 variable=self.volume, length=320).pack(side="left", padx=8)

        # --- Save button + status ---
        self.save_btn = tk.Button(root, text="Save as audio file…", command=self.on_save)
        self.save_btn.pack(pady=10)
        self.status = tk.Label(root, text="", fg="gray")
        self.status.pack()

    def on_save(self):
        text = self.text_box.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("No text", "Please enter some text first.")
            return

        # Native Save As dialog (prompts before overwriting an existing file).
        output_file = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV audio", "*.wav")],
            initialfile="speech.wav",
            title="Save audio as",
        )
        if not output_file:
            return  # user cancelled

        # Resolve the selected voice to its engine id.
        voice_id = None
        if self.voices:
            voice_id = self.voices[self.voice_choice.current()].id

        # Disable the button and run synthesis off the main thread.
        self.save_btn.config(state="disabled")
        self.status.config(text="Generating…", fg="gray")

        def worker():
            try:
                synthesize(text, output_file, self.rate.get(),
                           self.volume.get(), voice_id)
                self.root.after(0, self.on_done, output_file, None)
            except Exception as e:
                self.root.after(0, self.on_done, output_file, e)

        threading.Thread(target=worker, daemon=True).start()

    def on_done(self, output_file, error):
        self.save_btn.config(state="normal")
        if error:
            self.status.config(text="Failed.", fg="red")
            messagebox.showerror("Error", f"Could not save the file:\n{error}")
        else:
            self.status.config(text=f"Saved: {output_file}", fg="green")
            messagebox.showinfo("Done", f"Saved successfully:\n{output_file}")


if __name__ == "__main__":
    root = tk.Tk()
    TTSApp(root)
    root.mainloop()
