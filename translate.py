import subprocess
import torch
from transformers import MarianMTModel, MarianTokenizer

# 1. Model Configuration
device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "Helsinki-NLP/opus-mt-en-es"

tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name, use_safetensors=True).to(device)

# 2. Piper Paths (Adjust PIPER_BIN path if 'piper' is not in your PATH)
PIPER_BIN = "piper"  # Or full path like "/home/piyu/.../piper"
MODELO_ONNX = "en_US-ryan-high.onnx"

def translate_and_speak(text):
    # Step A: Translate text
    inputs = tokenizer(text, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        translated_tokens = model.generate(**inputs)
    translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
    
    print(f"[EN]: {text}")
    print(f"[ES]: {translated_text}")

    # Step B: Pipe Piper output directly to aplay for zero-latency audio playback
    # Piper outputs raw PCM audio to stdout, and aplay reads it from stdin
    piper_cmd = [PIPER_BIN, "--model", MODELO_ONNX, "--output-raw"]
    aplay_cmd = ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-q"]

    p_piper = subprocess.Popen(piper_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p_aplay = subprocess.Popen(aplay_cmd, stdin=p_piper.stdout)

    # Pass the translated text to Piper's stdin
    p_piper.stdin.write(text.encode("utf-8"))
    p_piper.stdin.close()
    
    p_aplay.wait()

if __name__ == "__main__":
    while True:
        user_input = input("\nEnter word or sentence (or 'q' to quit): ")
        if user_input.lower() == 'q':
            break
        if user_input.strip():
            translate_and_speak(user_input)