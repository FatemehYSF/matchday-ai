from PIL import Image, ImageDraw, ImageFont

SIZE = 1080
BACKGROUND = (12, 12, 16)   # almost black
WHITE = (245, 245, 245)


def font(size: int):
    try:
        return ImageFont.truetype("Arial Bold.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def centered(draw, y: int, text: str, fnt, fill) -> None:
    width = draw.textlength(text, font=fnt)
    draw.text(((SIZE - width) / 2, y), text, font=fnt, fill=fill)


def render_match_card(match, out_path: str) -> None:
    img = Image.new("RGB", (SIZE, SIZE), BACKGROUND)
    draw = ImageDraw.Draw(img)
    centered(draw, 390, f"{match.home_score} - {match.away_score}", font(200), WHITE)
    img.save(out_path)
