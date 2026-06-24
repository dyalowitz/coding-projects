import os, pyttsx3
engine = pyttsx3.init()
engine.save_to_file("Testing one two three.", "test.wav")
engine.runAndWait()
if os.path.exists("test.wav") and os.path.getsize("test.wav") > 0:
    print(f"PASS: test.wav written, {os.path.getsize('test.wav')} bytes")
else:
    print("FAIL: file missing or empty")
