import json
import os
from pathlib import Path
from rich.console import Console
import torch

console = Console()

def translate_json(json_path: str, output_folder: str, tokenizer, model, device: str) -> str:
    """Translates an English subtitle JSON to Spanish."""
    json_path_obj = Path(json_path)
    os.makedirs(output_folder, exist_ok=True)
    path_salida = os.path.join(output_folder, json_path_obj.name)

    console.print(f"\n[bold yellow]--- Translating: {json_path_obj.name} ---[/]")

    with open(json_path, "r", encoding="utf-8") as f:
        data_original = json.load(f)

    data_unida = []

    with torch.no_grad():
        for index, item in enumerate(data_original, start=1):
            texto_en = item.get("textEn", "").strip()

            if texto_en:
                inputs = tokenizer(
                    texto_en, return_tensors="pt", padding=True, truncation=True
                ).to(device)

                translated_tokens = model.generate(**inputs)
                texto_es = tokenizer.decode(
                    translated_tokens[0], skip_special_tokens=True
                )

                item_actualizado = {
                    "start": item.get("start"),
                    "end": item.get("end"),
                    "textEn": texto_en,
                    "textEs": texto_es,
                }
                data_unida.append(item_actualizado)

                if device == "cuda":
                    torch.cuda.empty_cache()

    with open(path_salida, "w", encoding="utf-8") as f:
        json.dump(data_unida, f, indent=4, ensure_ascii=False)

    console.print(f"[bold green]✓ Translation saved:[/] [cyan]{path_salida}[/]")
    return path_salida