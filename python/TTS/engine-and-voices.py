import pyttsx3
engine = pyttsx3.init()
voices = engine.getProperty("voices")
print(f"Engine initialized OK. {len(voices)} voice(s) found:")
for i, v in enumerate(voices):
    print(f"  [{i}] {v.name}")
