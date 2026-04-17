from pathlib import Path

from PIL import Image


BASE_DIR = Path(__file__).resolve().parent
png_path = BASE_DIR / "logo.png"
ico_path = BASE_DIR / "logo.ico"

if not png_path.exists():
    raise FileNotFoundError(
        "logo.png bulunamadı. Önce logo.svg dosyasını PNG'ye çevirip "
        "aynı klasöre logo.png olarak koy."
    )

img = Image.open(png_path).convert("RGBA")
img.save(
    ico_path,
    format="ICO",
    sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
)

print(f"Oluşturuldu: {ico_path}")