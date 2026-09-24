import subprocess
import torch
from transformers import MarianMTModel, MarianTokenizer

device = "cuda" if torch.cuda.is_available() else "cpu"

# 1. Load English -> Spanish Model
en_es_name = "Helsinki-NLP/opus-mt-en-es"
tokenizer_en_es = MarianTokenizer.from_pretrained(en_es_name)
model_en_es = MarianMTModel.from_pretrained(en_es_name, use_safetensors=True).to(device)

# 2. Load Spanish -> English Model
es_en_name = "Helsinki-NLP/opus-mt-es-en"
tokenizer_es_en = MarianTokenizer.from_pretrained(es_en_name)
model_es_en = MarianMTModel.from_pretrained(es_en_name, use_safetensors=True).to(device)

# 3. Piper Settings (English Voice)
PIPER_BIN = "piper"
MODELO_ONNX = "en_US-ryan-high.onnx"

def speak_english(english_text):
    """Sends English text to Piper TTS and plays it directly with aplay."""
    piper_cmd = [PIPER_BIN, "--model", MODELO_ONNX, "--output-raw"]
    aplay_cmd = ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-q"]

    p_piper = subprocess.Popen(piper_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p_aplay = subprocess.Popen(aplay_cmd, stdin=p_piper.stdout)

    p_piper.stdin.write(english_text.encode("utf-8"))
    p_piper.stdin.close()
    p_aplay.wait()

def translate(text, tokenizer, model):
    """Helper function to run MarianMT translation."""
    inputs = tokenizer(text, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        tokens = model.generate(**inputs)
    return tokenizer.decode(tokens[0], skip_special_tokens=True)

if __name__ == "__main__":
    mode = "1"  # Default mode: EN -> ES
    
    print("\n--- Translation Script initialized ---")
    print("Commands:")
    print("  '1' -> Switch to EN -> ES (Speaks input EN)")
    print("  '2' -> Switch to ES -> EN (Speaks translated EN)")
    print("  'q' -> Quit")

    while True:
        current_label = "EN -> ES" if mode == "1" else "ES -> EN"
        user_input = input(f"\n[{current_label}] Enter text: ").strip()

        if user_input.lower() == 'q':
            break
        elif user_input == '1':
            mode = "1"
            print("Switched to Mode 1: English to Spanish")
            continue
        elif user_input == '2':
            mode = "2"
            print("Switched to Mode 2: Spanish to English")
            continue

        if not user_input:
            continue

        if mode == "1":
            # EN -> ES
            translated_es = translate(user_input, tokenizer_en_es, model_en_es)
            print(f"[EN]: {user_input}")
            print(f"[ES]: {translated_es}")
            speak_english(user_input)
        else:
            # ES -> EN
            translated_en = translate(user_input, tokenizer_es_en, model_es_en)
            print(f"[ES]: {user_input}")
            print(f"[EN]: {translated_en}")
            speak_english(translated_en)