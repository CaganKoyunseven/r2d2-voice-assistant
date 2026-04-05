"""
Run once to generate the system tray icon:
    python assets/generate_icon.py
Produces: assets/r2d2_icon.png
"""
import os
from PIL import Image, ImageDraw

SIZE = 64
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "r2d2_icon.png")


def generate():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Body (blue-grey circle)
    draw.ellipse([4, 4, SIZE - 4, SIZE - 4], fill=(100, 140, 200, 255))

    # Head stripe (dark blue)
    draw.rectangle([4, 4, SIZE - 4, 22], fill=(40, 80, 160, 255))

    # Eye (white circle + black pupil)
    draw.ellipse([22, 8, 42, 20], fill=(255, 255, 255, 255))
    draw.ellipse([28, 10, 36, 18], fill=(20, 20, 20, 255))

    # Body detail lines
    draw.line([12, 30, SIZE - 12, 30], fill=(200, 220, 255, 200), width=2)
    draw.line([12, 38, SIZE - 12, 38], fill=(200, 220, 255, 200), width=2)

    img.save(OUT_PATH)
    print(f"Icon generated: {OUT_PATH}")


if __name__ == "__main__":
    generate()
