"""
Script para agregar fondo blanco a imágenes hasta resolución 560x800.
- Lee el array desde un archivo PHP de entrada (INPUT_PHP)
- Descarga y procesa cada imagen
- Redimensiona la imagen de entrada a RESIZE_W x RESIZE_H (manteniendo proporciones)
- Centra sobre un canvas blanco de TARGET_W x TARGET_H
- Guarda los archivos planos en OUTPUT_DIR con nombre saneado
- Genera un PHP de salida con la misma estructura originalSource
"""

import os
import re
import unicodedata
import requests
from PIL import Image
from io import BytesIO

# ── Configuración ────────────────────────────────────────────────────────────
INPUT_PHP   = "imagenes_input.php"   # archivo PHP con el array de entrada
OUTPUT_DIR  = "imagenes_padded"      # carpeta donde se guardan las imágenes
OUTPUT_PHP  = "imagenes_output.php"  # PHP generado con los nuevos nombres

# URL base que se concatena al originalSource en el PHP de salida
# Ejemplo: "https://midominio.com/imagenes/" → "https://midominio.com/imagenes/nombre-01.jpg"
URL_BASE    = "https://fc-images.vercel.app/imagenes_padded/" # dejar vacío si solo quieres el nombre de archivo

# Tamaño al que se redimensiona la imagen original antes de pegar en el canvas
RESIZE_W    = 621
RESIZE_H    = 776

# Tamaño final del canvas (imagen de salida)
TARGET_W    = 560
TARGET_H    = 800
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


def process_image(img: Image.Image, resize_w: int, resize_h: int,
                  target_w: int, target_h: int) -> Image.Image:
    """
    1. Redimensiona la imagen proporcionalmente para que quepa en resize_w x resize_h.
    2. Centra el resultado sobre un canvas blanco de target_w x target_h.
    """
    # Paso 1: redimensionar proporcionalmente al tamaño de entrada deseado
    img = img.copy()
    img.thumbnail((resize_w, resize_h), Image.LANCZOS)

    # Paso 2: centrar en el canvas final
    rw, rh = img.size
    canvas = Image.new("RGB", (target_w, target_h), (255, 255, 255))
    offset_x = (target_w - rw) // 2
    offset_y = (target_h - rh) // 2
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
    nfkd = unicodedata.normalize("NFD", name)
    clean = "".join(c for c in nfkd if not unicodedata.combining(c))
    clean = clean.replace(" ", "_")
    clean = re.sub(r"[^\w\-]", "", clean)
    clean = re.sub(r"_+", "_", clean)
    return clean.strip("_").lower()


def write_output_php(filepath: str, entries: list, url_base: str) -> None:
    """
    Escribe el array PHP de salida con la estructura:
        ["title"=>"...", "img"=>[["originalSource"=>"<url_base>nombre.jpg"], ...]]
    """
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("<?php\n\n$productos = [\n")
        for entry in entries:
            f.write('    [\n')
            f.write(f'        "title"=>"{entry["title"]}",\n')
            f.write('        "img"=>[\n')
            for fname in entry["files"]:
                f.write(f'            ["originalSource"=>"{url_base}{fname}"],\n')
            f.write('        ]\n')
            f.write('    ],\n')
        f.write("];\n")


# ── Main ─────────────────────────────────────────────────────────────────────
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Leyendo '{INPUT_PHP}'...")
products = parse_php_array(INPUT_PHP)
print(f"  → {len(products)} productos encontrados.")
print(f"  Redimensión previa : {RESIZE_W}x{RESIZE_H}")
print(f"  Canvas final       : {TARGET_W}x{TARGET_H}")
print(f"  URL base           : '{URL_BASE}'\n")

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
            result = process_image(img, RESIZE_W, RESIZE_H, TARGET_W, TARGET_H)
            result.save(filepath, "JPEG", quality=95)
            print(f"  ✓ {filename}  {img.size} → {result.size}")
            saved_files.append(filename)
            total += 1
        except Exception as e:
            print(f"  ✗ Error en '{filename}': {e}")
            errors += 1

    array_entries.append({"title": title, "files": saved_files})

write_output_php(OUTPUT_PHP, array_entries, URL_BASE)

print(f"\nListo.")
print(f"  {total} imágenes guardadas en '{OUTPUT_DIR}/'")
print(f"  {errors} errores")
print(f"  Array exportado en '{OUTPUT_PHP}'")
