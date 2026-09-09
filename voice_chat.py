import os
import subprocess
import tempfile
import numpy as np
import scipy.io.wavfile as wav
import sounddevice as sd
from faster_whisper import WhisperModel
import ollama

# Silenciar logs de ONNX
os.environ["ORT_LOGGING_LEVEL"] = "3"

# ==========================================
# CONFIGURACIÓN DE MODELOS Y RUTAS
# ==========================================
WHISPER_MODEL_SIZE = "base"
OLLAMA_MODEL = "llama3.2:latest" 

# Ruta al ejecutable de Piper y al modelo ONNX
PIPER_BIN = "./piper/piper"  # Ajusta la ruta a tu binario de piper
PIPER_MODEL_ONNX = "en_US-ryan-high.onnx"

SAMPLE_RATE_REC = 16000


def record_audio_prompt() -> str:
    """Graba audio desde el micrófono usando la tecla ENTER."""
    input("\n Presiona ENTER para empezar a hablar...")
    print(" Grabando... Presiona ENTER para detener.")
    
    audio_data = []
    state = {"recording": True}

    def callback(indata, frames, time_info, status):
        if state["recording"]:
            audio_data.append(indata.copy())

    with sd.InputStream(samplerate=SAMPLE_RATE_REC, channels=1, dtype='int16', callback=callback):
        input()  # Espera ENTER para frenar
        state["recording"] = False

    print(" Grabación finalizada.")

    if not audio_data:
        return None

    recording_array = np.concatenate(audio_data, axis=0)
    
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav.write(temp_wav.name, SAMPLE_RATE_REC, recording_array)
    return temp_wav.name


def transcribe_audio(whisper_model: WhisperModel, wav_path: str) -> str:
    """Convierte el audio a texto en inglés con faster-whisper."""
    segments, _ = whisper_model.transcribe(wav_path, language="en")
    text = " ".join([segment.text for segment in segments]).strip()
    return text

def speak_piper(text: str):
    """Sintetiza y reproduce el audio usando directamente el binario de Piper."""
    try:
        print(" [TTS] Sintetizando y reproduciendo voz...")
        
        # Archivo temporal para volcar la salida de audio de Piper
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_audio_path = temp_audio.name
        temp_audio.close()

        # Comando ejecutable de Piper
        cmd = [
            PIPER_BIN,
            "--model", PIPER_MODEL_ONNX,
            "--output_file", temp_audio_path
        ]

        # Pasamos el texto directamente por stdin al ejecutable de Piper
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        _, stderr = process.communicate(input=text)

        if process.returncode != 0:
            print(f" [TTS Error] Piper devolvió un error: {stderr}")
            return

        # Leer y reproducir con sounddevice
        samplerate, audio_data = wav.read(temp_audio_path)
        
        if len(audio_data) > 0:
            sd.play(audio_data, samplerate=samplerate)
            sd.wait()
            print(" [TTS] Reproducción finalizada.")
        else:
            print(" [TTS Warning] El archivo generado por Piper está vacío.")

    except Exception as e:
        print(f" [TTS Error] Ocurrió un error al ejecutar Piper: {e}")

    finally:
        if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


def main():
    print(" Cargando modelo Faster-Whisper...")
    whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")

    messages = [
    {
        "role": "system",
        "content": "You are an encouraging English conversation partner. "
                   "Keep responses short (2-3 sentences max) to give the user maximum speaking time. "
                   "If the user hesitates or uses simple terms to explain a complex idea, "
                   "naturally integrate the more precise word in your reply without formally correcting them."
    }
    ]

    print("\n Sistema listo. Presiona Ctrl+C para salir.")

    while True:
        try:
            # 1. Escuchar
            wav_file = record_audio_prompt()
            if not wav_file:
                continue

            # 2. Transcribir
            user_text = transcribe_audio(whisper_model, wav_file)
            if os.path.exists(wav_file):
                os.remove(wav_file)
            
            if not user_text:
                print("No se detectó voz. Intenta de nuevo.")
                continue

            print(f"\n You: {user_text}")

            # 3. Consultar a Ollama
            messages.append({"role": "user", "content": user_text})
            response = ollama.chat(model=OLLAMA_MODEL, messages=messages)
            ai_text = response['message']['content']
            
            messages.append({"role": "assistant", "content": ai_text})
            print(f"\n AI: {ai_text}")

            # 4. Reproducir respuesta
            speak_piper(ai_text)

        except KeyboardInterrupt:
            print("\n ¡Conversación finalizada!")
            break

if __name__ == "__main__":
    main()