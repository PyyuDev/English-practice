import sys
import os
import requests
from odf.opendocument import OpenDocumentText, load
from odf.text import P

# Configuración
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:latest"                # Cambiá por tu modelo local de Ollama
PIPER_BIN = "piper"                    # Ruta al ejecutable de Piper si no está en PATH
MODELO_ONNX = "en_US-ryan-high.onnx" # Cambiá por la ruta real a tu archivo .onnx

def extract_all_text(node):
  text = []
  for child in node.childNodes:
    if hasattr(child, "data") and child.data:
      text.append(child.data)
    elif child.hasChildNodes():
      text.append(extract_all_text(child))
  return "".join(text)


def leer_odt(ruta):
  doc = load(ruta)
  elementos = doc.getElementsByType(P)
  return "\n".join(extract_all_text(el) for el in elementos)

def guardar_odt(texto, ruta_salida):
    doc = OpenDocumentText()
    for linea in texto.split("\n"):
        if linea.strip():
            p = P(text=linea)
            doc.text.addElement(p)
    doc.save(ruta_salida)

def corregir_con_ollama(texto):
    prompt = (
        "You are an expert English proofreader. Correct the following text for grammar, "
        "spelling, and natural phrasing. Output ONLY the corrected text, without explanations, "
        f"quotes, or introductory text:\n\n{texto}"
    )
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code == 200:
        return response.json().get("response", "").strip()
    else:
        raise Exception(f"Error al conectar con Ollama: {response.text}")

def texto_a_audio(texto, ruta_audio):
    # Uso de subprocess para pasar el texto a Piper evitando problemas de escape en shell
    import subprocess
    comando = [PIPER_BIN, "--model", MODELO_ONNX, "--output_file", ruta_audio]
    proceso = subprocess.Popen(comando, stdin=subprocess.PIPE, text=True)
    proceso.communicate(input=texto)

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 corregir_y_locutar_odt.py <archivo.odt>")
        sys.exit(1)

    archivo_entrada = sys.argv[1]
    nombre_base = os.path.splitext(archivo_entrada)[0]
    archivo_salida_odt = f"{nombre_base}_corregido.odt"
    archivo_salida_wav = f"{nombre_base}_audio.wav"

    print("📖 Leyendo archivo .odt...")
    texto_original = leer_odt(archivo_entrada)
    print(texto_original)

    print("🤖 Corrigiendo inglés con Ollama...")
    texto_corregido = corregir_con_ollama(texto_original)

    print(f"💾 Guardando texto corregido en '{archivo_salida_odt}'...")
    guardar_odt(texto_corregido, archivo_salida_odt)

    print("🗣️ Generando audio con Piper TTS...")
    texto_a_audio(texto_corregido, archivo_salida_wav)

    print("\n✅ ¡Proceso completado!")
    print(f"- Archivo ODT corregido: {archivo_salida_odt}")
    print(f"- Audio generado: {archivo_salida_wav}")

if __name__ == "__main__":
    main()