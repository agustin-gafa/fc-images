"""
Script para agregar fondo blanco a imágenes hasta resolución 560x800.
- Lee el array desde un archivo PHP de entrada (INPUT_PHP)
- Descarga y procesa cada imagen
- Guarda los archivos planos en OUTPUT_DIR con nombre "Título - 01.jpg"
- Genera un PHP de salida con la misma estructura originalSource pero con el nuevo nombre de archivo
"""

import os
import re
import requests
from PIL import Image
from io import BytesIO

# ── Configuración ────────────────────────────────────────────────────────────
INPUT_PHP  = "imagenes_input.php"   # archivo PHP con el array de entrada
OUTPUT_DIR = "imagenes_padded"      # carpeta donde se guardan las imágenes
OUTPUT_PHP = "imagenes_output.php"  # PHP generado con los nuevos nombres
TARGET_W   = 560
TARGET_H   = 800
# ─────────────────────────────────────────────────────────────────────────────


def parse_php_array(filepath: str) -> list:
    """
    Parsea el array PHP de entrada y devuelve una lista de dicts:
      [{"title": "...", "urls": ["url1", "url2"]}, ...]
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    products = []

    block_pattern = re.compile(
        r'\[\s*"title"\s*=>\s*"([^"]+)"\s*,\s*"img"\s*=>\s*\[(.*?)\]\s*\]',
        re.DOTALL
    )
    url_pattern = re.compile(r'"originalSource"\s*=>\s*"([^"]+)"')

    for block in block_pattern.finditer(content):
        title = block.group(1)
        img_block = block.group(2)
        urls = url_pattern.findall(img_block)
        products.append({"title": title, "urls": urls})

    return products


def pad_image(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Centra la imagen en un canvas blanco de target_w x target_h sin redimensionar."""
    orig_w, orig_h = img.size
    if orig_w > target_w or orig_h > target_h:
        img.thumbnail((target_w, target_h), Image.LANCZOS)
        orig_w, orig_h = img.size

    canvas = Image.new("RGB", (target_w, target_h), (255, 255, 255))
    offset_x = (target_w - orig_w) // 2
    offset_y = (target_h - orig_h) // 2
    canvas.paste(img, (offset_x, offset_y))
    return canvas


def sanitize(name: str) -> str:
    """
    Limpia el título para usarlo como nombre de archivo:
    - Elimina acentos y diacríticos
    - Reemplaza espacios por guiones bajos
    - Elimina cualquier carácter que no sea alfanumérico, guion o guion bajo
    - Convierte a minúsculas
    """
    import unicodedata
    nfkd = unicodedata.normalize("NFD", name)
    ascii_str = "".join(c for c in nfkd if not unicodedata.combining(c))
    ascii_str = ascii_str.replace(" ", "_")
    ascii_str = re.sub(r"[^\w\-]", "", ascii_str)
    ascii_str = re.sub(r"_+", "_", ascii_str)
    return ascii_str.strip("_").lower()


def write_output_php(filepath: str, entries: list) -> None:
    """
    Escribe el array PHP de salida con la estructura:
        ["title"=>"...", "img"=>[["originalSource"=>"nombre.jpg"], ...]]
    """
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("<?php\n\n$productos = [\n")
        for entry in entries:
            f.write('    [\n')
            f.write(f'        "title"=>"{entry["title"]}",\n')
            f.write('        "img"=>[\n')
            for fname in entry["files"]:
                f.write(f'            ["originalSource"=>"{fname}"],\n')
            f.write('        ]\n')
            f.write('    ],\n')
        f.write("];\n")


# ── Main ─────────────────────────────────────────────────────────────────────
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Leyendo '{INPUT_PHP}'...")
products = parse_php_array(INPUT_PHP)
print(f"  → {len(products)} productos encontrados.\n")

total = 0
errors = 0
array_entries = []

for product in products:
    title = product["title"]
    base_name = sanitize(title)
    saved_files = []

    for i, url in enumerate(product["urls"], start=1):
        filename = f"{base_name}-0{i}.jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGB")
            result = pad_image(img, TARGET_W, TARGET_H)
            result.save(filepath, "JPEG", quality=95)
            print(f"  ✓ {filename}")
            saved_files.append(filename)
            total += 1
        except Exception as e:
            print(f"  ✗ Error en '{filename}': {e}")
            errors += 1

    array_entries.append({"title": title, "files": saved_files})

write_output_php(OUTPUT_PHP, array_entries)

print(f"\nListo.")
print(f"  {total} imágenes guardadas en '{OUTPUT_DIR}/'")
print(f"  {errors} errores")
print(f"  Array exportado en '{OUTPUT_PHP}'")
