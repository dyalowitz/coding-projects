import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pyttsx3


def synthesize_STUB(text, output_file, rate, volume, voice_id, voice_name):
    """Fake synthesis: prints what it received, sleeps to mimic real work."""
    print("--- synthesize() would have been called with: ---")
    print(f"  text     : {text!r}")
    print(f"  output   : {output_file}")
    print(f"  rate     : {rate}")
    print(f"  volume   : {volume}")
    print(f"  voice    : {voice_name}  (id={voice_id})")
    print("  ...simulating 2 seconds of work...")
    time.sleep(2)
    print("--- stub finished ---")


class TTSApp:
    def __init__(self, root):
        self.root = root
        root.title("Text to Speech  [TEST MODE — no audio]")
        root.geometry("520x440")
        root.resizable(False, False)

        try:
            probe = pyttsx3.init()
            self.voices = probe.getProperty("voices")
        except Exception as e:
            messagebox.showerror("Error", f"Could not start the speech engine:\n{e}")
            self.voices = []

        pad = {"padx": 12, "pady": 6}

        tk.Label(root, text="Enter text to convert:").pack(anchor="w", **pad)
        self.text_box = tk.Text(root, height=8, wrap="word")
        self.text_box.pack(fill="x", padx=12)
        self.text_box.insert("1.0", "This is a test of the text to speech function.")

        voice_frame = tk.Frame(root)
        voice_frame.pack(fill="x", **pad)
        tk.Label(voice_frame, text="Voice:").pack(side="left")
        self.voice_names = [v.name for v in self.voices] or ["(default)"]
        self.voice_choice = ttk.Combobox(
            voice_frame, values=self.voice_names, state="readonly", width=40
        )
        self.voice_choice.current(0)
        self.voice_choice.pack(side="left", padx=8)

        rate_frame = tk.Frame(root)
        rate_frame.pack(fill="x", **pad)
        tk.Label(rate_frame, text="Speed:").pack(side="left")
        self.rate = tk.IntVar(value=180)
        tk.Scale(rate_frame, from_=80, to=300, orient="horizontal",
                 variable=self.rate, length=320).pack(side="left", padx=8)

        vol_frame = tk.Frame(root)
        vol_frame.pack(fill="x", **pad)
        tk.Label(vol_frame, text="Volume:").pack(side="left")
        self.volume = tk.DoubleVar(value=1.0)
        tk.Scale(vol_frame, from_=0.0, to=1.0, resolution=0.1, orient="horizontal",
                 variable=self.volume, length=320).pack(side="left", padx=8)

        self.save_btn = tk.Button(root, text="Save as audio file…", command=self.on_save)
        self.save_btn.pack(pady=10)
        self.status = tk.Label(root, text="", fg="gray")
        self.status.pack()

    def on_save(self):
        text = self.text_box.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("No text", "Please enter some text first.")
            return

        output_file = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV audio", "*.wav")],
            initialfile="speech.wav",
            title="Save audio as",
        )
        if not output_file:
            return

        voice_id = None
        voice_name = "(default)"
        if self.voices:
            idx = self.voice_choice.current()
            voice_id = self.voices[idx].id
            voice_name = self.voices[idx].name

        self.save_btn.config(state="disabled")
        self.status.config(text="Generating… (test mode)", fg="gray")

        def worker():
            try:
                synthesize_STUB(text, output_file, self.rate.get(),
                                self.volume.get(), voice_id, voice_name)
                self.root.after(0, self.on_done, output_file, None)
            except Exception as e:
                self.root.after(0, self.on_done, output_file, e)

        threading.Thread(target=worker, daemon=True).start()

    def on_done(self, output_file, error):
        self.save_btn.config(state="normal")
        if error:
            self.status.config(text="Failed.", fg="red")
            messagebox.showerror("Error", f"Stub error:\n{error}")
        else:
            self.status.config(text=f"(test) would have saved: {output_file}", fg="green")
            messagebox.showinfo("Done (test mode)",
                                f"No audio written.\nWould have saved:\n{output_file}")


if __name__ == "__main__":
    root = tk.Tk()
    TTSApp(root)
    root.mainloop()
