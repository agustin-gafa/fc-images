# Crear y activar el entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install Pillow requests

# Ejecutar el script
python pad_images.py

# Al terminar, desactivar el entorno
deactivate