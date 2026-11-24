import textwrap
from PIL import Image, ImageDraw, ImageFont

SIZE = 1080
BACKGROUND = (12, 12, 16)   # almost black
WHITE = (245, 245, 245)
ACCENT = (0, 230, 118)    # bright green, like a football brand colour
GREY = (150, 150, 160)    # soft grey for less important text
ACCENT = (0, 230, 118)    # bright green, like a football brand colour
GREY = (150, 150, 160)    # soft grey for less important text


def font(size: int):
    try:
        return ImageFont.truetype("Arial Bold.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def centered(draw, y: int, text: str, fnt, fill) -> None:
    width = draw.textlength(text, font=fnt)
    draw.text(((SIZE - width) / 2, y), text, font=fnt, fill=fill)


def render_match_card(match, caption, out_path):
    img = Image.new("RGB", (SIZE, SIZE), BACKGROUND)
    draw = ImageDraw.Draw(img)

    # Top: green bar, competition, FULL TIME
    draw.rectangle([0, 0, SIZE, 14], fill=ACCENT)
    centered(draw, 70, match.competition.upper(), font(40), GREY)
    centered(draw, 130, "FULL TIME", font(56), ACCENT)

    # Middle: teams and the big score
    centered(draw, 300, match.home_team, font(64), WHITE)
    centered(draw, 390, f"{match.home_score} - {match.away_score}", font(200), WHITE)
    centered(draw, 640, match.away_team, font(64), WHITE)

    # Bottom: goal scorers (max 2 lines)
    if match.goals:
        scorers = ", ".join(f"{g.player} {g.minute}'" for g in match.goals)
        for i, line in enumerate(textwrap.wrap(scorers, width=55)[:2]):
            centered(draw, 750 + i * 40, line, font(28), GREY)
        # Bottom: the AI caption (emojis removed: most fonts can't draw them)
    clean = "".join(ch for ch in caption if ord(ch) < 0x2000).strip()
    for i, line in enumerate(textwrap.wrap(clean, width=48)[:3]):
        centered(draw, 880 + i * 46, line, font(34), WHITE)

    img.save(out_path)

