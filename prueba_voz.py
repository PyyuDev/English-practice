import sounddevice as sd
import soundfile as sf
import whisper

SAMPLE_RATE = 16000
DURATION = 30
AUDIO_FILE = "prueba.wav"

# 1. Grabación
print("🎤 Grabando 5 segundos...")
audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
sd.wait()
sf.write(AUDIO_FILE, audio, SAMPLE_RATE)
print("✅ Grabación finalizada.")

# 2. Reproducción del audio grabado
"""print("🔊 Reproduciendo tu grabación...")
sd.play(audio, SAMPLE_RATE)
sd.wait()"""  # Espera a que termine la reproducción antes de continuar

# 3. Transcripción con Whisper
print("🚀 Procesando transcripción en GPU...")
model = whisper.load_model("base")
result = model.transcribe(AUDIO_FILE, language="en")

print("\n--- RESULTADO ---")
print("Texto:", result["text"])