"""
Script para agregar fondo blanco a imágenes hasta resolución 560x800
Sin redimensionar, solo añade padding blanco al rededor.
"""

import os
import requests
from PIL import Image, ImageOps
from io import BytesIO

TARGET_W = 560
TARGET_H = 800
OUTPUT_DIR = "imagenes_padded"
ARRAY_FILE = "imagenes_array.php"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Lista de imágenes extraída del array original
images = [
    {"title": "Calcetín de canalé de caña corta - azul oficina", "urls": ["https://estatico1.four-cottons.com/5138-large_default/calcetin-de-canale-de-cana-corta.jpg", "https://estatico1.four-cottons.com/5139-large_default/calcetin-de-canale-de-cana-corta.jpg"]},
    {"title": "Calcetín de canalé de caña corta - azul petróleo melange", "urls": ["https://estatico1.four-cottons.com/4499-large_default/calcetin-de-canale-de-cana-corta.jpg", "https://estatico1.four-cottons.com/4498-large_default/calcetin-de-canale-de-cana-corta.jpg"]},
    {"title": "Calcetín de canalé de caña corta - verde thyme", "urls": ["https://estatico1.four-cottons.com/5146-large_default/calcetin-de-canale-de-cana-corta.jpg", "https://estatico1.four-cottons.com/5147-large_default/calcetin-de-canale-de-cana-corta.jpg"]},
    {"title": "Calcetín de canalé de caña corta - azul notte", "urls": ["https://estatico1.four-cottons.com/5448-large_default/calcetin-de-canale-de-cana-corta.jpg", "https://estatico1.four-cottons.com/5449-large_default/calcetin-de-canale-de-cana-corta.jpg"]},
    {"title": "Calcetín de canalé de caña corta - caldero melange", "urls": ["https://estatico1.four-cottons.com/5523-large_default/calcetin-de-canale-de-cana-corta.jpg", "https://estatico1.four-cottons.com/5524-large_default/calcetin-de-canale-de-cana-corta.jpg"]},
    {"title": "Calcetín de canalé de caña corta - verde oliva melange", "urls": ["https://estatico1.four-cottons.com/5543-large_default/calcetin-de-canale-de-cana-corta.jpg", "https://estatico1.four-cottons.com/5544-large_default/calcetin-de-canale-de-cana-corta.jpg"]},
    {"title": "Calcetín de canalé de caña corta - verde campo melange", "urls": ["https://estatico1.four-cottons.com/5541-large_default/calcetin-de-canale-de-cana-corta.jpg", "https://estatico1.four-cottons.com/5542-large_default/calcetin-de-canale-de-cana-corta.jpg"]},
    {"title": "Calcetín de canalé de caña corta - Cuio", "urls": ["https://estatico1.four-cottons.com/5247-large_default/calcetin-de-canale-de-cana-corta.jpg", "https://estatico1.four-cottons.com/5248-large_default/calcetin-de-canale-de-cana-corta.jpg"]},
    {"title": "Calcetín de canalé de caña corta - azul marino melange", "urls": ["https://estatico1.four-cottons.com/5521-large_default/calcetin-de-canale-de-cana-corta.jpg", "https://estatico1.four-cottons.com/5522-large_default/calcetin-de-canale-de-cana-corta.jpg"]},
    {"title": "Calcetín de canalé de caña corta - tierra melange", "urls": ["https://estatico1.four-cottons.com/5539-large_default/calcetin-de-canale-de-cana-corta.jpg", "https://estatico1.four-cottons.com/5540-large_default/calcetin-de-canale-de-cana-corta.jpg"]},
    {"title": "Calcetín de canalé de caña alta bicolor - Rayas Azul notte - Terra", "urls": ["https://estatico1.four-cottons.com/5519-large_default/calcetin-de-canale.jpg", "https://estatico1.four-cottons.com/5520-large_default/calcetin-de-canale.jpg"]},
    {"title": "Calcetín de canalé de caña alta bicolor - Viola - Verde campo", "urls": ["https://estatico1.four-cottons.com/4648-large_default/calcetin-de-canale.jpg", "https://estatico1.four-cottons.com/4647-large_default/calcetin-de-canale.jpg"]},
    {"title": "Calcetín de canalé de caña alta bicolor - Antracita melange - Fiume", "urls": ["https://estatico1.four-cottons.com/5115-large_default/calcetin-de-canale.jpg", "https://estatico1.four-cottons.com/5116-large_default/calcetin-de-canale.jpg"]},
    {"title": "Calcetín de canalé de caña alta bicolor - Sabana tostado", "urls": ["https://estatico1.four-cottons.com/5585-large_default/calcetin-de-canale.jpg", "https://estatico1.four-cottons.com/5586-large_default/calcetin-de-canale.jpg"]},
    {"title": "Calcetín de canalé de caña alta bicolor - Corda - azul oceano", "urls": ["https://estatico1.four-cottons.com/4987-large_default/calcetin-de-canale.jpg", "https://estatico1.four-cottons.com/4988-large_default/calcetin-de-canale.jpg"]},
    {"title": "Calcetín de canalé de caña alta bicolor - Verde oscuro - Vino", "urls": ["https://estatico1.four-cottons.com/4594-large_default/calcetin-de-canale.jpg", "https://estatico1.four-cottons.com/4593-large_default/calcetin-de-canale.jpg"]},
    {"title": "Calcetín de canalé de caña alta bicolor - Rayas Verde erika - Azul", "urls": ["https://estatico1.four-cottons.com/5617-large_default/calcetin-de-canale.jpg", "https://estatico1.four-cottons.com/5618-large_default/calcetin-de-canale.jpg"]},
    {"title": "Calcetín de canalé de caña alta bicolor - Azul Petroleo - Rossastro", "urls": ["https://estatico1.four-cottons.com/5737-large_default/calcetin-de-canale.jpg", "https://estatico1.four-cottons.com/5738-large_default/calcetin-de-canale.jpg"]},
    {"title": "Calcetín de canalé de caña alta bicolor - Verde Campo - Antracite", "urls": ["https://estatico1.four-cottons.com/5741-large_default/calcetin-de-canale.jpg", "https://estatico1.four-cottons.com/5742-large_default/calcetin-de-canale.jpg"]},
    {"title": "Calcetín de canalé de caña alta bicolor - Verde oliva - Azul melange", "urls": ["https://estatico1.four-cottons.com/4638-large_default/calcetin-de-canale.jpg", "https://estatico1.four-cottons.com/5787-large_default/calcetin-de-canale.jpg"]},
    {"title": "Calcetín de canalé de caña alta bicolor - Negro oficina", "urls": ["https://estatico1.four-cottons.com/4636-large_default/calcetin-de-canale.jpg", "https://estatico1.four-cottons.com/4635-large_default/calcetin-de-canale.jpg"]},
    {"title": "Calcetín de canalé de caña alta bicolor - Azul oficina", "urls": ["https://estatico1.four-cottons.com/4620-large_default/calcetin-de-canale.jpg", "https://estatico1.four-cottons.com/4619-large_default/calcetin-de-canale.jpg"]},
]


def pad_image(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Centra la imagen en un canvas blanco de target_w x target_h sin redimensionar."""
    # Si la imagen es más grande que el target en alguna dimensión, la redimensionamos
    # proporcionalmente solo para que quepa (opcional: quitar esto si NO quieres reducir)
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
    """Limpia el título para usarlo como nombre de archivo."""
    return "".join(c if c.isalnum() or c in " -_" else "_" for c in name).strip()


total = 0
errors = 0
array_entries = []

for product in images:
    title = product["title"]
    base_name = sanitize(title)
    saved_files = []

    for i, url in enumerate(product["urls"], start=1):
        filename = f"{base_name} - 0{i}.jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content)).convert("RGB")
            result = pad_image(img, TARGET_W, TARGET_H)
            result.save(filepath, "JPEG", quality=95)
            print(f"✓ {filename}")
            saved_files.append(filename)
            total += 1
        except Exception as e:
            print(f"✗ Error en '{filename}': {e}")
            errors += 1

    array_entries.append({"title": title, "files": saved_files})

# Generar archivo PHP con el array actualizado
with open(ARRAY_FILE, "w", encoding="utf-8") as f:
    f.write("<?php\n\n$productos = [\n")
    for entry in array_entries:
        f.write(f'    [\n')
        f.write(f'        "title" => "{entry["title"]}",\n')
        f.write(f'        "img" => [\n')
        for fname in entry["files"]:
            f.write(f'            ["filename" => "{fname}"],\n')
        f.write(f'        ]\n')
        f.write(f'    ],\n')
    f.write("];\n")

print(f"\nListo. {total} imágenes guardadas en '{OUTPUT_DIR}/', {errors} errores.")
print(f"Array generado en '{ARRAY_FILE}'")
