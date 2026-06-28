import random
import string
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CHARS = string.ascii_uppercase + string.digits  # A-Z + 0-9
CAPTCHA_LENGTH = 8
IMG_WIDTH = 320
IMG_HEIGHT = 60
CHAR_W = 38   # largeur réservée par caractère
CHAR_H = 60   # hauteur complète de l'image

_FONT_PATHS = [
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/cour.ttf",
    "C:/Windows/Fonts/times.ttf",
]
_font_cache: dict[int, ImageFont.ImageFont] = {}


def _load_font(size: int = 36) -> ImageFont.ImageFont:
    if size not in _font_cache:
        for path in _FONT_PATHS:
            try:
                _font_cache[size] = ImageFont.truetype(path, size)
                break
            except Exception:
                continue
        else:
            _font_cache[size] = ImageFont.load_default()
    return _font_cache[size]


def generate_captcha(
    text: str | None = None,
    hard: bool = False,
) -> tuple[Image.Image, str, list[int]]:
    """
    Retourne (image 200x60, texte, liste des positions x de chaque caractère).
    hard=False : CAPTCHAs simples pour l'entraînement.
    hard=True  : version distordue pour la démo.
    """
    if text is None:
        text = ''.join(random.choices(CHARS, k=CAPTCHA_LENGTH))

    bg = (random.randint(230, 255), random.randint(230, 255), random.randint(230, 255))
    img = Image.new('RGB', (IMG_WIDTH, IMG_HEIGHT), color=bg)
    draw = ImageDraw.Draw(img)
    font = _load_font(36)

    char_x_positions: list[int] = []
    x = 8
    for char in text:
        char_x_positions.append(x)
        color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))

        if hard:
            char_img = Image.new('RGBA', (44, 54), (255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_img)
            char_draw.text((4, 4), char, font=font, fill=(*color, 255))
            rotated = char_img.rotate(random.randint(-25, 25), expand=False, fillcolor=(255, 255, 255, 0))
            img.paste(rotated, (x, random.randint(0, 8)), rotated)
        else:
            y = random.randint(4, 14)
            draw.text((x, y), char, font=font, fill=color)

        x += CHAR_W

    n_lines = random.randint(4, 7) if hard else random.randint(1, 3)
    n_dots  = random.randint(150, 300) if hard else random.randint(30, 80)

    for _ in range(n_lines):
        lc = (random.randint(80, 200), random.randint(80, 200), random.randint(80, 200))
        draw.line(
            [(random.randint(0, IMG_WIDTH), random.randint(0, IMG_HEIGHT)),
             (random.randint(0, IMG_WIDTH), random.randint(0, IMG_HEIGHT))],
            fill=lc, width=1,
        )
    for _ in range(n_dots):
        draw.point(
            (random.randint(0, IMG_WIDTH - 1), random.randint(0, IMG_HEIGHT - 1)),
            fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
        )

    img = img.filter(ImageFilter.SMOOTH)
    return img, text, char_x_positions


def crop_character(img: Image.Image, x: int) -> Image.Image:
    """Découpe la région d'un caractère depuis l'image complète."""
    x1 = max(0, x - 2)
    x2 = min(IMG_WIDTH, x + CHAR_W)
    return img.crop((x1, 0, x2, IMG_HEIGHT))
